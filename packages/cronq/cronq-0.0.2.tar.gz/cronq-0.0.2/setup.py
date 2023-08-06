#!/usr/bin/env python
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def run_setup():
    setup(
        name='cronq',
        version='0.0.2',
        description='A Cron-like system for running tasks',
        keywords = 'cron amqp',
        url='http://github.com/philipcristiano/cronq',
        author='Philip Cristiano',
        author_email='philipcristiano@gmail.com',
        license='BSD',
        packages=['cronq', 'cronq.backends'],
        install_requires=[
            'haigha',
            'sqlalchemy',
            'mysql-connector-python',
        ],
        test_suite='tests',
        long_description=read('README.md'),
        zip_safe=True,
        classifiers=[
        ],
        entry_points="""
        [console_scripts]
           cronq-runner=cronq.runner:main
           cronq-injector=cronq.injector:main
        """,
    )

if __name__ == '__main__':
    run_setup()
