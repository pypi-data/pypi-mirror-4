import os
from setuptools import setup, find_packages

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='surebilling',
    version='1.0',
    author='SureBilling Inc.',
    author_email='admin@surebilling.com',
    description='Python wrapper for the SureBilling API',
    long_description=read('README'),
    url='http://surebilling.com',
    packages=find_packages(),
#    install_requires=['pyactiveresource==1.0.1'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: Other/Proprietary License',
        'Topic :: Office/Business :: Financial :: Accounting',
    ],
)
