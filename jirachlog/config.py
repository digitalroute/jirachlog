import os
import sys
import logging

class Config:
    jira_username = 'user'
    jira_password = 'pass'
    jira_server = 'http://localhost'
    git_revision_range = None
    git_cwd = None
    git_log_pattern = r"(.*)\s(DAZ-\d+):\s?(.*)"

    def __init__(self):
        if "JIRA_USERNAME" in os.environ and os.environ['JIRA_USERNAME']:
            self.jira_username = os.environ['JIRA_USERNAME']
        if "JIRA_PASSWORD" in os.environ and os.environ['JIRA_PASSWORD']:
            self.jira_password = os.environ['JIRA_PASSWORD']
        if "JIRA_SERVER" in os.environ and os.environ['JIRA_SERVER']:
            self.jira_server = os.environ["JIRA_SERVER"]
        
        if (len(sys.argv) < 3):
            print('Usage: %s <revision-range> "<release name in Jira>"' % sys.argv[0])
            sys.exit(1)

        self.git_revision_range = sys.argv[1]

        self.release = sys.argv[2]

        self.git_cwd = os.getcwd()
        if len(sys.argv) > 3 and sys.argv[3]:
            self.git_cwd = sys.argv[3]
