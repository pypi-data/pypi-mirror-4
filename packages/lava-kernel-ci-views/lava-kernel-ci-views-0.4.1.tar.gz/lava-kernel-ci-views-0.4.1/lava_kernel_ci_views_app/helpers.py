

from collections import defaultdict, namedtuple
import contextlib
import datetime
import re

from dashboard_app.models import DataView, TestResult

DAY_DELTA = datetime.timedelta(days=1)
WEEK_DELTA = datetime.timedelta(days=7)

def fetchnamed(cursor):
    class cls(object):
        pass
    names = ' '.join(col[0] for col in cursor.description)
    typ = namedtuple('result', names)
    for row in cursor.fetchall():
        yield typ(*row)


index_sql = """
select softwaresource.branch_url as git_url,
       softwaresource.branch_revision as git_commit_id,
       coalesce(namedattribute_git_describe.value, softwaresource.branch_revision) as git_describe,
       coalesce(namedattribute_git_log_info.value, softwaresource.branch_revision) as git_log_info,
       namedattribute_gitweb_url.value as gitweb_url,
       softwaresource.commit_timestamp as commit_timestamp,
       testrun.analyzer_assigned_date as build_date,
       namedattribute_kernelconfig.value as config,
       testresult.result as result,
       namedattribute_kernelbuild_url.value as build_url,
       bundle.content_sha1 as bundle_sha1
  from dashboard_app_bundlestream as bundlestream,
       dashboard_app_bundle as bundle,
       dashboard_app_testresult as testresult,
       dashboard_app_testrun as testrun
inner join dashboard_app_namedattribute AS namedattribute_kernelconfig
        on (namedattribute_kernelconfig.object_id = testrun.id
            and namedattribute_kernelconfig.name = 'kernel.config'
            and namedattribute_kernelconfig.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
inner join dashboard_app_namedattribute AS namedattribute_kernelbuild_url
        on (namedattribute_kernelbuild_url.object_id = testrun.id
            and namedattribute_kernelbuild_url.name = 'kernel.build_url'
            and namedattribute_kernelbuild_url.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
left outer join dashboard_app_namedattribute as namedattribute_git_describe
        on (namedattribute_git_describe.object_id = testrun.id
            and namedattribute_git_describe.name = 'kernel.git_describe_info'
            and namedattribute_git_describe.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
left outer join dashboard_app_namedattribute as namedattribute_git_log_info
        on (namedattribute_git_log_info.object_id = testrun.id
            and namedattribute_git_log_info.name = 'kernel.git_log_info'
            and namedattribute_git_log_info.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
left outer join dashboard_app_namedattribute as namedattribute_gitweb_url
        on (namedattribute_gitweb_url.object_id = testrun.id
            and namedattribute_gitweb_url.name = 'kernel.gitweb_url'
            and namedattribute_gitweb_url.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
left outer join dashboard_app_namedattribute as namedattribute_target_device_type
        on (namedattribute_target_device_type.object_id = testrun.id
            and namedattribute_target_device_type.name = 'target.device_type'
            and namedattribute_target_device_type.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            ),
       dashboard_app_softwaresource as softwaresource,
       dashboard_app_testrun_sources as tr_ss_link
 where bundle.bundle_stream_id = bundlestream.id
   and testrun.bundle_id = bundle.id
   and softwaresource.id = tr_ss_link.softwaresource_id
   and testrun.id = tr_ss_link.testrun_id
   and bundlestream.slug like 'ci-linux%%-build'
   and testresult.test_run_id = testrun.id
   and %s < testrun.analyzer_assigned_date and testrun.analyzer_assigned_date < %s
"""

find_builds_sql = """
select testresult.result as result,
       namedattribute_kernelbuild_url.value as build_url,
       namedattribute_targethostname.value as targethostname,
       testcase.test_case_id as test_case_id,
       test.test_id as test_id,
       testresult.relative_index as result_index,
       testrun.analyzer_assigned_uuid as uuid
  from dashboard_app_bundlestream as bundlestream,
       dashboard_app_bundle as bundle,
       dashboard_app_testresult as testresult,
       dashboard_app_testcase as testcase,
       dashboard_app_testrun as testrun
inner join dashboard_app_namedattribute AS namedattribute_targethostname
        on (namedattribute_targethostname.object_id = testrun.id
            and namedattribute_targethostname.name = 'target.hostname'
            and namedattribute_targethostname.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
inner join dashboard_app_namedattribute AS namedattribute_kernelbuild_url
        on (namedattribute_kernelbuild_url.object_id = testrun.id
            and namedattribute_kernelbuild_url.name = 'kernel.build_url'
            and namedattribute_kernelbuild_url.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            ),
       dashboard_app_test as test
 where bundle.bundle_stream_id = bundlestream.id
   and testrun.bundle_id = bundle.id
   and bundlestream.slug like 'ci-linux%%'
   and testresult.test_run_id = testrun.id
   and testresult.test_case_id = testcase.id
   and test.id = testrun.test_id
   and namedattribute_kernelbuild_url.value = ANY(%s)
"""

# We display a lot of data on these pages, with a somewhat demented level of
# nesting:

# DayCollection ->* Day ->* Tree ->* Commit ->* Build ->* LavaRun ->* Result

# DayCollection: all the days for which we are displaying data
# Day: one day for which we are displaying data
# Tree: a kernel tree which was tested on the given day
#       (actually when a tree is tested on some days but not others, we insert
#       a 'null' tree on the days it was not tested to make the columns come
#       out right)
# Commit: a commit of the tree which was built on the given day
# Build: an attempt to build a defconfig of the tree on ci.linaro.org

# The above data is all that's displayed on the compile-focused view.

# LavaRun: a test of the built kernel in LAVA

# Result: The result of a part of the test in LAVA, such as successful booting
#         or 34/40 ltp tests passing.

# Although all of the levels are potentially 1 to many, many are not in
# practice.

# DayCollection ->* Day: always 1 to many, days (and their contents) are
#                        displayed as rows

# Day ->* Tree: usually 1 to many, trees are displayed as columns

# Tree ->* Commit: usually only 1 to 1, a commit is displayed as a row

# Commit ->* Build: 1 to 1 on a board page, 1 to many on the compile page,
#                   builds are displayed as "bubbles" sitting on top of the
#                   commits

# Build ->* LavaRun: always 1 to 1 in practice.  The LavaRun sits on top of
#                    the Build 'bubble', although the LavaRun itself has no
#                    visual representation (we just render the results).  If
#                    this was 1 to N by some miracle, the different lava runs
#                    would site side by side.

# LavaRun ->* Result: usually 1 to many.  Each result is rendered as a bubble,
#                     following the page-wide pattern of the later results
#                     being higher up.


class Result(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self._results = defaultdict(int)

    def add_result(self, result):
        self._results[result] += 1

    def json_ready(self):
        passes = self._results[TestResult.RESULT_PASS]
        total = sum(self._results.values())
        if passes != total:
            result = 'fail'
        else:
            result = 'pass'
        return {
            'passes': passes,
            'total': total,
            'result': result,
            'name': self.name,
            'link': self.link,
            }


class LavaRun(object):
    def __init__(self, board_class, build):
        self._board_class = board_class
        self.build = build
        self._lava_results = {}
        self._other_results = {}

    def add_result(self, test_run_id, test_case_name, result_code, result_index,
                 test_run_uuid):
        if test_run_id == 'lava':
            link = test_run_uuid + '/result/' + str(result_index)
            result = self._lava_results[result_index] = Result(test_case_name, link)
            result.add_result(result_code)
        else:
            if test_run_id not in self._other_results:
                self._other_results[test_run_id] = Result(test_run_id, test_run_uuid)
            result = self._other_results[test_run_id]
            result.add_result(result_code)

    def json_ready(self):
        lava_results = [result.json_ready()
                        for (index, result) in sorted(self._lava_results.items())]
        results = []
        testcase2index = {}
        for index, result in enumerate(lava_results):
            if result['result'] == 'pass':
                if result['name'] in ['deploy_linaro_image',
                                      'job_complete',
                                      'gather_results',
                                      'boot_image']:
                    continue
            else:
                if result['name'] not in ['boot_linaro_image']:
                    result['result'] = 'skip'
            testcase_name_match = re.match(
                'lava_test_run \(([-_A-Za-z0-9]+)\)', result['name'])
            if testcase_name_match:
                testcase_name = testcase_name_match.group(1)
                testcase2index[testcase_name] = index
                if testcase_name in self._other_results:
                    continue
            results.append(result)
        other_results = [result.json_ready()
                         for result in self._other_results.values()]
        other_results.sort(key=lambda d:testcase2index.get(d['name'], 0))
        results.extend(other_results)
        results.reverse()
        return {
            'board_class': self._board_class,
            'results': results,
            }


class Build(object):

    def __init__(self, config, result, sha1, commit):
        self._config = config
        self._result = result
        self._lava_runs = {}
        self.sha1 = sha1
        self.commit = commit
    @property
    def tests(self):
        return self._tests.values()
    def json_ready(self):
        lava_runs = [run.json_ready()
                     for (board_class, run) in sorted(self._lava_runs.iteritems())]
        if self._result:
            result = 'fail'
        else:
            result = 'pass'
        return {
            'config': self._config,
            'result': result,
            'lava_runs': lava_runs,
            'result_count': sum(len(run['results']) for run in lava_runs),
            'sha1': self.sha1,
            }
    def add_test(self, board_class, test_run_id, test_case_name, result, result_index, test_run_uuid):
        if board_class in self._lava_runs:
            run = self._lava_runs[board_class]
        else:
            run = self._lava_runs[board_class] = LavaRun(board_class, self)
        run.add_result(test_run_id, test_case_name, result, result_index, test_run_uuid)
    def find_test(self, board_class):
        return self._tests.get(board_class)


class Commit(object):
    def __init__(self, sha1, commit_timestamp, describe, log_info, gitweb_url, tree):
        self.sha1 = sha1
        self.commit_timestamp = commit_timestamp
        self.describe = describe
        self._builds = []
        self.log_info = log_info
        self.gitweb_url = gitweb_url
        self.tree = tree
    def add_build(self, config, result, sha1):
        build = Build(config, result, sha1, self)
        self.tree.day.daycollection._configs.add(config)
        self._builds.append(build)
        return build
    def find_builds(self, config):
        for build in self._builds:
            if build._config == config:
                yield build
    @property
    def builds(self):
        return list(self._builds)
    def json_ready(self):
        builds = [build.json_ready() for build in self._builds]
        def sort_key(build):
            return build['config']
        builds.sort(key=sort_key)
        for build in builds:
            build['width'] = (100.0 - len(builds) + 1)/len(builds)
        if self.prev:
            prev = self.prev.sha1
        else:
            prev = None
        commit_url = shortlog_url = None
        if self.gitweb_url:
            if 'github' in self.gitweb_url:
                base_url = self.gitweb_url
                if base_url.endswith('.git'):
                    base_url = base_url[:-len('.git')]
                commit_url = base_url + '/commit/' + self.sha1
            else:
                commit_url = self.gitweb_url + ';a=commit;h=' + self.sha1
                if self.prev:
                    shortlog_url = '%s;a=shortlog;h=%s;hp=%s' % (
                        self.gitweb_url, self.sha1, self.prev.sha1)
        return {
            'sha1': self.sha1,
            'describe': self.describe,
            'builds': builds,
            'max_results': max([build['result_count'] for build in builds] + [0]),
            'prev': prev,
            'log_info': self.log_info,
            'commit_url': commit_url,
            'shortlog_url': shortlog_url,
            }


class Tree(object):
    def __init__(self, git_url, index, day):
        self._git_url = git_url
        self._commits = {}
        self.day = day
        self.index = index
    def get_commit(self, sha1, commit_timestamp, describe, log_info, gitweb_url):
        if sha1 in self._commits:
            # XXX if self._commits[sha1].commit_timestamp != commit_timestamp ...
            return self._commits[sha1]
        else:
            commit_obj = self._commits[sha1] = Commit(
                sha1, commit_timestamp, describe, log_info, gitweb_url, self)
            return commit_obj
    @property
    def commits(self):
        return self._commits.values()
    def json_ready(self):
        def key(commit):
            return commit.commit_timestamp
        commits = self._commits.values()
        commits.sort(key=key)
        commits.reverse()
        commits = [commit.json_ready() for commit in commits]
        return {
            'name': self._git_url,
            'commits': commits,
            'max_results': max([commit['max_results'] for commit in commits] + [0]),
            'index': self.index,
            }


class Day(object):
    def __init__(self, day, daycollection):
        self._day = day
        self._trees = {}
        self.daycollection = daycollection
    def get_tree(self, git_url, index):
        if git_url in self._trees:
            return self._trees[git_url]
        else:
            tree_obj = self._trees[git_url] = Tree(git_url, index, self)
            return tree_obj
    @property
    def trees(self):
        return self._trees.values()
    def json_ready(self):
        # XXX how do we order trees?
        trees = [tree.json_ready() for tree in self._trees.values()]
        for tree in trees:
            tree['width'] = (100.0 - len(trees) + 1)/len(trees)
        trees.sort(key=lambda tree:tree['name'])
        return {
            'date': self._day.strftime('%A %B %d %Y'),
            'trees': trees,
            'max_results': max([tree['max_results'] for tree in trees] + [0]),
            }


class DayCollection(object):
    def __init__(self, board_type, start, finish):
        self.board_type = board_type
        self.start = start
        self.finish = finish
        self._days = {}
        # We create a Day object for every day we're interested in, plus one
        # day older so that we can find the previous build for the last row of
        # builds displayed.  This isn't quite enough, because the previous
        # build might have been more than one day before the last one
        # displayed, but for now it's a reasonable hack.
        d = start - DAY_DELTA
        while d < finish:
            self._days[d] = Day(d, self)
            d += DAY_DELTA
        self._board_classes = set()
        self._configs = set()
        self._urls_to_builds = {}
        self._tree2index = {}
        self.all_trees = set()

    def get_day(self, datestamp):
        day = datestamp.date()
        return self._days[day]

    def add_build(self, build_results):
        day = self.get_day(build_results.build_date)
        git_url = build_results.git_url
        if git_url not in self._tree2index:
            self._tree2index[git_url] = len(self._tree2index)
        tree = day.get_tree(git_url, self._tree2index[git_url])
        self.all_trees.add(tree)
        commit = tree.get_commit(
            build_results.git_commit_id, build_results.commit_timestamp,
            build_results.git_describe, build_results.git_log_info, build_results.gitweb_url)
        config = build_results.config
        if config.endswith('_defconfig'):
            config = config[:-len('_defconfig')]
        self._configs.add(config)
        build = commit.add_build(
            config, build_results.result, build_results.bundle_sha1)
        build_url = build_results.build_url
        if build_url != 'unknown':
            self._urls_to_builds[build_url] = build

    def add_test(self, test_result):
        board_class = test_result.targethostname.strip('0123456789')
        self._board_classes.add(board_class)
        self._urls_to_builds[test_result.build_url].add_test(
            board_class, test_result.test_id, test_result.test_case_id,
            test_result.result, test_result.result_index, test_result.uuid)

    def compute_prevs(self):
        # tree_commits maps git urls to Commit objects in the order they were
        # built.  Notice that it's not only possibly but likely that there
        # will be more than one Commit for a given git_commit_id (and hence
        # commit_timestamp) because we run builds daily even if the tip hasn't
        # changed.

        tree_commits = defaultdict(list)
        for day in sorted(self.days, key=lambda day:day._day):
            for tree in day.trees:
                commits = tree.commits
                commits.sort(key=lambda commit: commit.commit_timestamp)
                tree_commits[tree._git_url].extend(commits)
        for commits_list in tree_commits.values():
            if commits_list:
                commits_list.sort(key=lambda commit: commit.commit_timestamp)
                commits_list[0].prev = None
                for i in range(1, len(commits_list)):
                    commits_list[i].prev = commits_list[i-1]


    def evaluate(self, fetch_builds):
        connection = DataView.get_connection()
        with contextlib.closing(connection.cursor()) as cursor:
            sql = index_sql
            sql_args = (self.start - DAY_DELTA, self.finish)
            if self.board_type:
                sql += '   and namedattribute_target_device_type.value = %s'
                sql_args += (self.board_type,)
            cursor.execute(sql, sql_args)

            for build_result in fetchnamed(cursor):
                self.add_build(build_result)

            if fetch_builds:
                cursor.execute(find_builds_sql, (self._urls_to_builds.keys(),))

                for test_result in fetchnamed(cursor):
                    self.add_test(test_result)

        self.compute_prevs()

        self.fill_in_missing_trees()

    def fill_in_missing_trees(self):
        for day in self.days:
            missing_trees = self.all_trees - set(day.trees)
            for tree in missing_trees:
                day.get_tree(tree._git_url, self._tree2index[tree._git_url])

    @property
    def days(self):
        return self._days.values()

    def json_ready(self):
        def key(day_obj):
            return day_obj._day
        day_objs = self._days.values()
        day_objs.sort(key=key)
        day_objs.reverse()
        # Remove the extra day (see __init__ for the comment about this).
        del day_objs[-1]
        trees = []
        for url, index in sorted(self._tree2index.items()):
            trees.append({
                'url': url,
                'index': index,
                'width': (100.0 - len(self._tree2index) + 1)/len(self._tree2index)
                })
        days = [day_obj.json_ready() for day_obj in day_objs]
        for day in days:
            for tree in day['trees']:
                for commit in tree['commits']:
                    for build in commit['builds']:
                        build['dummy_results'] = range(day['max_results'] - build['result_count'])
        return {
            'days': days,
            'trees': trees,
            }

