import sys
import os
import subprocess
import re
from io import StringIO

from jira import JIRA

# status = {'self': 'https://jira.digitalroute.com/rest/api/2/status/10014', 'description': '', 'iconUrl': 'https://jira.digitalroute.com/images/icons/statuses/closed.png', 'name': 'Done', 'id': '10014', 'statusCategory': {'self': 'https://jira.digitalroute.com/rest/api/2/statuscategory/3', 'id': 3, 'key': 'done', 'colorName': 'green', 'name': 'Done'}}

class IssueInfo:
    def __init__(self, issue, summary, status, part_of_release):
        self.issue = issue
        self.summary = summary
        self.status = status
        self.part_of_release = part_of_release
    
    def get_status(self):
        if self.status != 'Done':
            return '**' + self.status + '**'
        else:
            return self.status

# A dictionary of jira issues -> array of git hashes
jira_issues_git_hashes = dict()

# these are ALL jira issues we've fetched which includes issues and subtasks
jira_issues_summary = dict()

# Dictionary of git hash -> log message
git_hash_log = dict()

# Jira issues parents pointing to childs
jira_issues_parents = dict()

def parse(config):
    jira = JIRA(basic_auth=(config.jira_username, config.jira_password), options={'server': config.jira_server})

    cmd = subprocess.Popen(['git', 'log', '--oneline', '--no-color', config.git_revision_range], cwd=config.git_cwd, stdout=subprocess.PIPE)
    for line in cmd.stdout:
        match = re.search(config.git_log_pattern, str(line.decode('utf-8').rstrip()))
        if match:
            matched_hash = match.group(1)
            matched_issue = match.group(2)
            matched_log = match.group(3)

            git_hash_log[matched_hash] = matched_log

            if matched_issue not in jira_issues_git_hashes:
                jira_issues_git_hashes[matched_issue] = []
            jira_issues_git_hashes[matched_issue].append(matched_hash)

            if matched_issue not in jira_issues_summary:
                issue = jira.issue(matched_issue)
                if hasattr(issue, 'fields'):
                    jira_issues_summary[matched_issue] = IssueInfo(matched_issue, issue.fields.summary, issue.fields.status.name, match_version(config.release, issue))
                    if hasattr(issue.fields, 'parent'):
                        parentIssue = jira.issue(issue.fields.parent)
                        if hasattr(parentIssue, 'fields'):
                            jira_issues_summary[parentIssue.key] = IssueInfo(matched_issue, parentIssue.fields.summary, parentIssue.fields.status.name, match_version(config.release, issue))
                            if parentIssue.key not in jira_issues_parents:
                                jira_issues_parents[parentIssue.key] = []
                            jira_issues_parents[parentIssue.key].append(matched_issue)
                    else:
                        jira_issues_parents[matched_issue] = []

#
# Return true if it's part of the current release
#
# Here is the JIRA response which we parse:
# fixVersions =  [{'self': 'https://jira.digitalroute.com/rest/api/2/version/15524', 'id': '15524', 'description': 'Release 154 - Sprint 154 deliverables', 'name': 'Release 154', 'archived': False, 'released': False, 'releaseDate': '2019-07-19'}],
#
def match_version(release, issue):
    if hasattr(issue, 'fields') and hasattr(issue.fields, 'fixVersions'):
        for version in issue.fields.fixVersions:
            if version.name == release:
                return True
    return False

def print_issue(buffer, issue):
    issue_info = jira_issues_summary[issue]
    buffer.write("* %s (%s) %s\n" % (issue, issue_info.get_status(), issue_info.summary))
    if issue in jira_issues_git_hashes:
        for hash in jira_issues_git_hashes[issue]:
            buffer.write("  * %s %s\n" % (hash, git_hash_log[hash]))
    return

def print_sub_issue(buffer, issue):
    issue_info = jira_issues_summary[issue]
    buffer.write("  * %s (%s) %s\n" % (issue, issue_info.get_status(), issue_info.summary))
    if issue in jira_issues_git_hashes:
        for hash in jira_issues_git_hashes[issue]:
            buffer.write("    * %s %s\n" % (hash, git_hash_log[hash]))
    return

def print_issues(config):
    buffer = StringIO()

    for issue in sorted(jira_issues_parents):
        issue_info = jira_issues_summary[issue]
        if issue_info.part_of_release:
            print_issue(buffer, issue)
            for subIssue in sorted(jira_issues_parents[issue]):
                print_sub_issue(buffer, subIssue)

    if buffer.getvalue() != "":
        print("### %s" % config.release)
        print()
        print(buffer.getvalue())

    buffer = StringIO()

    for issue in sorted(jira_issues_parents):
        issue_info = jira_issues_summary[issue]
        if not issue_info.part_of_release:
            print_issue(buffer, issue)
            for subIssue in sorted(jira_issues_parents[issue]):
                print_sub_issue(buffer, subIssue)

    if buffer.getvalue() != "":
        print("### Not part of release")
        print()
        print(buffer.getvalue())

def git_log(git_revision_range, cwd):
    cmd = subprocess.Popen(['git', 'log', '--oneline', '--no-color', git_revision_range], cwd=cwd, stdout=subprocess.PIPE)
    return cmd.stdout
