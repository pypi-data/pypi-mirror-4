#-*- coding: utf-8 -*-

from setuptools import setup

requires = ['requests', 'simplejson']

setup(
    name="walletkit",
    version="1.0.1",
    author="Walletkit",
    author_email="support@walletkit.com",
    description="Walletkit Python SDK",
    url="http://walletkit.com/docs/sdk/python",
    packages=['walletkit'],
    install_requires=requires,
    setup_requires=requires,
)
