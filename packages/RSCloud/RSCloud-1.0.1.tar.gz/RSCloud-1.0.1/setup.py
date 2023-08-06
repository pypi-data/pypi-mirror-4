import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "RSCloud",
    version = "1.0.1",
    packages = ['rscloud','rscloud.bin'],
    scripts = ['distribute_setup.py'],
    install_requires = ['requests>=1.1.0', 'pytz>=2012j', 'python-dateutil>=2.1','simplejson>=3.0.7','keyring>=1.2','PyYAML>=3.10','MySQL-python>=1.2.4'],
    author = "Rackspace SMB Operations",
    author_email = ["Nathan.House@RACKSPACE.com","Samuel.Stavinoha@RACKSPACE.com","Zak.Jones@RACKSPACE.com"],
    description = "Rackspace Cloud Python Bindings",
    license = "Apache License 2.0",
    keywords = ['rackspace', 'cloud', 'python bindings'],
    url = "http://pypi.python.org/pypi/RSCloud",
    include_package_data = True,
    classifiers=[
	  'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development',
	         ],
    
     )
