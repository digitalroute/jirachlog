# jirachlog

## Introduction

Creates a basic changelog using git and Jira

## Prerequisites

Make sure you have Python3.

## Installation

Run command:

    pip3 install jirachlog

## Deploy new version to PyPi

This should be done by CI soon.

    python setup.py bdist_wheel
    python -m twine upload dist/jirachlog-1.0.0-py3-none-any.whl
