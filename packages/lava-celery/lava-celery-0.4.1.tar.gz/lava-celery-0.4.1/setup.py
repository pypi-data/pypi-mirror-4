#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='lava-celery',
    version=":versiontools:lava.celery:",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@linaro.org",
    namespace_packages=['lava'],
    packages=find_packages(),
    test_suite="unittest2.collector",
    license="AGPL",
    description="Celery integration for LAVA Server",
    entry_points="""
    [lava.commands]
    celery = lava.celery.commands:celery
    celeryd = lava.celery.commands:celeryd
    celery-schedulermonitor- = lava.celery.commands:celery_schedulermonitor
    [lava.celery.commands]
    run-remote= lava.celery.commands:run_remote
    hello-world = lava.celery.commands:hello_world
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    extras_require={
        'client': [
            'lava-tool > 0.4'
        ]
    },
    install_requires=[
        'versiontools >= 1.8',
        'celery >= 2.0'
    ],
    setup_requires=[
        'versiontools >= 1.8',
    ],
    tests_require=[
        'unittest2'
    ],
    zip_safe=False,
    include_package_data=True
)

