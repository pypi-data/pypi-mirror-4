#
# Copyright (c) 2006-2013, Prometheus Research, LLC
#


#
# To install HTSQL-PGSQL, run `python setup.py install`.
#


from setuptools import setup
import os.path


NAME = "HTSQL-PGSQL"
VERSION = "2.3.3"
DESCRIPTION = "A Database Query Language (PostgreSQL backend)"
LONG_DESCRIPTION = open(os.path.join(os.path.dirname(__file__),
                                     "README")).read()
AUTHOR = "Clark C. Evans and Kirill Simonov; Prometheus Research, LLC"
AUTHOR_EMAIL = "cce@clarkevans.com, xi@resolvent.net"
LICENSE = "AGPLv3 or Permissive for use with Open Source databases"
KEYWORDS = "sql relational database query language"
PLATFORMS = "Any"
URL = "http://htsql.org/"
CLASSIFIERS = """
""".strip().splitlines() or None
PACKAGE_DIR = {'': 'src'}
INCLUDE_PACKAGE_DATA = True
ZIP_SAFE = False
PACKAGES = """
htsql_pgsql
htsql_pgsql.tweak
htsql_pgsql.core
htsql_pgsql.tweak.inet
htsql_pgsql.tweak.timeout
htsql_pgsql.tweak.system
htsql_pgsql.core.tr
""".strip().splitlines()
INSTALL_REQUIRES = """
HTSQL
psycopg2
""".strip().splitlines()
CONSOLE_SCRIPTS = """
""".strip().splitlines() or None
HTSQL_ROUTINES = """
""".strip().splitlines() or None
HTSQL_ADDONS = """
engine.pgsql = htsql_pgsql.core:EnginePGSQLAddon
tweak.inet.pgsql = htsql_pgsql.tweak.inet:TweakINetPGSQLAddon
tweak.system.pgsql = htsql_pgsql.tweak.system:TweakSystemPGSQLAddon
tweak.timeout.pgsql = htsql_pgsql.tweak.timeout:TweakTimeoutPGSQLAddon
""".strip().splitlines() or None
ENTRY_POINTS = {}
if CONSOLE_SCRIPTS:
    ENTRY_POINTS['console_scripts'] = CONSOLE_SCRIPTS
if HTSQL_ROUTINES:
    ENTRY_POINTS['htsql.routines'] = HTSQL_ROUTINES
if HTSQL_ADDONS:
    ENTRY_POINTS['htsql.addons'] = HTSQL_ADDONS


setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      keywords=KEYWORDS,
      platforms=PLATFORMS,
      url=URL,
      classifiers=CLASSIFIERS,
      package_dir=PACKAGE_DIR,
      include_package_data=INCLUDE_PACKAGE_DATA,
      zip_safe=ZIP_SAFE,
      packages=PACKAGES,
      install_requires=INSTALL_REQUIRES,
      entry_points=ENTRY_POINTS)


