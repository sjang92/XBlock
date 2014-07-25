"""Set up for XBlock"""
from setuptools import setup

setup(
    name='XBlock',
    version='0.4a1',
    description='XBlock Core Library',
    packages=[
        'xblock',
        'xblock.django',
        'xblock.reference',
    ],
    install_requires=[
        'lxml',
        'webob',
        'pytz',
        'python-dateutil',
    ]
)
