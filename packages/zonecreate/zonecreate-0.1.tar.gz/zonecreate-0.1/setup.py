import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGES')).read()

requires = [
        'mako',
    ]

setup(name='zonecreate',
      version='0.1',
      description='zonecreate are some helper scripts for generating zone files',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Operating System :: Unix",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: System Administrators",
        ],
      author='Bert JW Regeer',
      author_email='bertjw@regeer.org',
      url='https://github.com/bertjwregeer/zonecreate',
      keywords='dns zones',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='',
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      zone_create = zonecreate.zone_create:main
      zone_update_soa = zonecreate.zone_update_soa:main
      zone_add_record = zonecreate.zone_add_record:main
      zone_del_record = zonecreate.zone_del_record:main
      """,
      )

