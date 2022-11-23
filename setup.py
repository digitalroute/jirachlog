from setuptools import setup

exec(open('jirachlog/ver.py').read())

with open('README.md') as file:
    long_description = file.read()

setup(name='jirachlog',
    version=__version__,
    description='Creates a basic changelog using git and Jira',
    author="Marcus Johansson",
    author_email="polarn@gmail.com",
    long_description=long_description,
    license='APACHE',
    url='https://github.com/digitalroute/jirachlog',
    packages=['jirachlog'],
    scripts=['bin/jirachlog'],
    zip_safe=False,
    install_requires=[
        'jira>=3.0.0'
    ],
)
