import sys
import os
import subprocess
import re
from jira import JIRA

# A dictionary of jira issues -> array of git hashes
jira_issues_git_hashes = dict()

# these are ALL jira issues we've fetched which includes issues and subtasks
jira_issues_summary = dict()

# Dictionary of git hash -> log message
git_hash_log = dict()

# Jira issues parents pointing to childs
jira_issues_parents = dict()

def parse(jira_username, jira_password, jira_server, git_revision_range, git_cwd, git_log_pattern):

    jira = JIRA(basic_auth=(jira_username, jira_password), options={'server': jira_server})

    cmd = subprocess.Popen(['git', 'log', '--oneline', '--no-color', git_revision_range], cwd=git_cwd, stdout=subprocess.PIPE)
    for line in cmd.stdout:
        match = re.search(git_log_pattern, str(line.decode('utf-8').rstrip()))
        if match:
            marched_hash = match.group(1)
            matched_issue = match.group(2)
            matched_log = match.group(3)

            git_hash_log[marched_hash] = matched_log

            if matched_issue not in jira_issues_git_hashes:
                jira_issues_git_hashes[matched_issue] = []
            jira_issues_git_hashes[matched_issue].append(marched_hash)

            if matched_issue not in jira_issues_summary:
                issue = jira.issue(matched_issue)
                if hasattr(issue, 'fields'):
                    summary = issue.fields.summary
                    jira_issues_summary[matched_issue] = summary
                    if hasattr(issue.fields, 'parent'):
                        parentIssue = jira.issue(issue.fields.parent)
                        if hasattr(parentIssue, 'fields'):
                            summary = parentIssue.fields.summary
                            jira_issues_summary[parentIssue.key] = summary
                            if parentIssue.key not in jira_issues_parents:
                                jira_issues_parents[parentIssue.key] = []
                            jira_issues_parents[parentIssue.key].append(matched_issue)
                    else:
                        jira_issues_parents[matched_issue] = []


def print_issue(issue):
    summary = jira_issues_summary[issue]
    print("* %s %s" % (issue, summary))
    if issue in jira_issues_git_hashes:
        for hash in jira_issues_git_hashes[issue]:
            print("  * %s %s" % (hash, git_hash_log[hash]))
    return

def print_sub_issue(issue):
    summary = jira_issues_summary[issue]
    print("  * %s %s" % (issue, summary))
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
