import sys
import os
import subprocess
import re
from jira import JIRA

class IssueInfo:
    def __init__(self, issue, summary, status):
        self.issue = issue
        self.summary = summary
        self.status = status

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
                    jira_issues_summary[matched_issue] = IssueInfo(matched_issue, issue.fields.summary, issue.fields.status)
                    if hasattr(issue.fields, 'parent'):
                        parentIssue = jira.issue(issue.fields.parent)
                        if hasattr(parentIssue, 'fields'):
                            jira_issues_summary[parentIssue.key] = IssueInfo(matched_issue, parentIssue.fields.summary, parentIssue.fields.status)
                            if parentIssue.key not in jira_issues_parents:
                                jira_issues_parents[parentIssue.key] = []
                            jira_issues_parents[parentIssue.key].append(matched_issue)
                    else:
                        jira_issues_parents[matched_issue] = []

def print_issue(issue):
    issue_info = jira_issues_summary[issue]
    print("* %s (%s) %s" % (issue, issue_info.status, issue_info.summary))
    if issue in jira_issues_git_hashes:
        for hash in jira_issues_git_hashes[issue]:
            print("  * %s %s" % (hash, git_hash_log[hash]))
    return

def print_sub_issue(issue):
    issue_info = jira_issues_summary[issue]
    print("  * %s (%s) %s" % (issue, issue_info.status, issue_info.summary))
    if issue in jira_issues_git_hashes:
        for hash in jira_issues_git_hashes[issue]:
            print("    * %s %s" % (hash, git_hash_log[hash]))
    return

def print_issues():
    for issue in sorted(jira_issues_parents):
        print_issue(issue)
        for subIssue in sorted(jira_issues_parents[issue]):
            print_sub_issue(subIssue)


def git_log(git_revision_range, cwd):
    cmd = subprocess.Popen(['git', 'log', '--oneline', '--no-color', git_revision_range], cwd=cwd, stdout=subprocess.PIPE)
    return cmd.stdout
