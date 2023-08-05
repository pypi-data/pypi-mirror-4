from setuptools import setup, find_packages
import subprocess

def get_long_desc():
    """Use Pandoc to convert the readme to ReST for the PyPI."""
    try:
        return subprocess.check_output(['pandoc', '-f', 'markdown', '-t', 'rst', 'README.mdown'])
    except:
        print "WARNING: The long readme wasn't converted properly"

setup(name='django-icybackup',
    version='0.1pre1',
    description='A Django database/media backup tool with Amazon Glacier and local folder support',
    long_description=get_long_desc(),
    author='Adam Brenecki, St Barnabas\' Theological College',
    author_email='abrenecki@sbtc.org.au',
    url='https://github.com/stbarnabas/django-icybackup',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=[
        'setuptools_git>=0.3',
    ],
    install_requires=[
        'boto',
    ],
)
