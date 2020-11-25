# jirachlog

## Introduction

Creates a basic changelog using git and Jira

## Prerequisites

Make sure you have Python3.

## Installation

Run command:

    pip3 install jirachlog

## Development

Create and activate virtual environment:

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

Test the binary: (you can use your own Jira user)

    PYTHONPATH=. JIRA_SERVER="https://jira.digitalroute.com/" JIRA_USERNAME=xxxx JIRA_PASSWORD=yyyy ./bin/jirachlog v1.5.0..v1.6.0 "Release 175 - Stream Linking" /Users/marcusj/code/dazzlerjs/dazzlerjs-api

You can test the module by installing it locally:

    python setup.py bdist_wheel
    /usr/local/bin/pip3 install ./dist/jirachlog-x.x.x-py3-none-any.whl

Reason for full path to pip3 is because we're in a virtual envirionment when doing python development

### Deploy new version to PyPi

This should be done by CI soon.

    python setup.py bdist_wheel
    python -m twine upload dist/jirachlog-x.x.x-py3-none-any.whl
