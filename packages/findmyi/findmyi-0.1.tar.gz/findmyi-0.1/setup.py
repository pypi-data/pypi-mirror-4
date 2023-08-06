try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='findmyi',
    packages=['findmyi'],  # this must be the same as the name above
    version='0.1',
    description='A simple Python interface to Find My iPhone over the iCloud service',
    author='Raphael Mutschler',
    author_email='info@raphaelmutschler.de',
    url='https://bitbucket.com/raphaelmutschler/fmi',   # use the URL to the github repo
    download_url='https://bitbucket.com/raphaelmutschler/fmi/get/master.tar.gz',  # I'll explain this in a second
    keywords=['find my iphone', 'apple', 'icloud'],  # arbitrary keywords
    install_requires=['requests==0.14.1'],
)
