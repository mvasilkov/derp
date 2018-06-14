from locale import strcoll

from integlib import common_defs
from integlib.jenkins import BuildNoLongerQueued
from integlib.runtime import runtime
from integlib.version import Version

IGNORED_ISSUES = frozenset(common_defs.EXCLUDED_INTEG_ISSUES)

PRIORITIES = {
    'Blocker': 1,
    'Critical': 2,
    'Major': 3,
    'Minor': 4,
    'Trivial': 5,
    None: 6,
}


def issue_running_or_pending(issue, jenkins_job: str = common_defs.UPSTREAM_JOB) -> bool:
    upstream_job = runtime.jenkins.get_job(jenkins_job)

    for build in upstream_job.get_queued_builds():
        try:
            param_issue = build.get_params().get('ISSUE')
            if issue.key == param_issue:
                # queued builds have no build_id
                return True
        except BuildNoLongerQueued:
            continue

    for build in upstream_job.get_builds():
        if build.is_running():
            param_issue = build.get_params().get('ISSUE')
            if issue.key == param_issue:
                build_id = getattr(build, 'build_id', None)
                if build_id is not None:
                    issue.props['jenkins_job'] = jenkins_job
                    issue.props['jenkins_build_id'] = build_id
                    issue.save()
                return True

    return False


def compare_issues_infinidat(a, b) -> int:
    'Compare issues'

    try:
        fix_version_a = Version(min(a.fix_versions))
        fix_version_b = Version(min(b.fix_versions))
        result = fix_version_a._compare(fix_version_b)
        if result:
            return result
    except:  # cannot compare versions
        pass

    result = PRIORITIES[a.priority] - PRIORITIES[b.priority]
    if result:
        return result

    return strcoll(a.key, b.key)
