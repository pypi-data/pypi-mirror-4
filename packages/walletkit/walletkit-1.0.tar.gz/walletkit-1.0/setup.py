from setuptools import setup,find_packages

    
requires = ['requests','simplejson']


setup(name = "walletkit",version = 1.0,scripts=['walletkit.py'],install_requires=requires,setup_requires=requires,description = "Walletkit Api",author="walletkit",author_email = "support@walletkit.com",url ="https://github.com/walletkit/python-sdk",py_modules=['walletkit'])


