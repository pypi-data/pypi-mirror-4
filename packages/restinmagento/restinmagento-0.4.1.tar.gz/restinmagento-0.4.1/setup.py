from setuptools import setup, find_packages
import sys, os


py_version = sys.version_info[:2]

PY3 = py_version[0] == 3

version = '0.4.1'

tests_require = []

if not PY3:
    tests_require.append('mock')

setup(name='restinmagento',
      version=version,
      description="REST client for the magento platform",
      long_description="""\
""",
      classifiers = [
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords=["REST", "Magento", "client"],
      author='Emmanuel Cazenave',
      author_email='emmanuel.cazenave@jmsinfor.com',
      url='https://bitbucket.org/jmsi/restinmagento',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=True,
      test_suite='restinmagento.tests',
      tests_require = tests_require,
      install_requires=[
        'requests',
        'requests_oauthlib',
        'simplejson',
      ],
      entry_points={
        'console_scripts': [
            'rim-tmptoken = restinmagento.scripts:tmptoken',
            'rim-resourcetoken= restinmagento.scripts:resourcetoken',
            ],
        },
     
      )
