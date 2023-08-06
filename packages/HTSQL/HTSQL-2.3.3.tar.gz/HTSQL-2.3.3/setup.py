#
# Copyright (c) 2006-2013, Prometheus Research, LLC
#


#
# To install HTSQL, run `python setup.py install`.
#


from setuptools import setup
import os.path


NAME = "HTSQL"
VERSION = "2.3.3"
DESCRIPTION = "A Database Query Language (core & SQLite backend)"
LONG_DESCRIPTION = open(os.path.join(os.path.dirname(__file__),
                                     "README")).read()
AUTHOR = "Clark C. Evans and Kirill Simonov; Prometheus Research, LLC"
AUTHOR_EMAIL = "cce@clarkevans.com, xi@resolvent.net"
LICENSE = "AGPLv3 or Permissive for use with Open Source databases"
KEYWORDS = "sql relational database query language"
PLATFORMS = "Any"
URL = "http://htsql.org/"
CLASSIFIERS = """
Development Status :: 4 - Beta
Environment :: Console
Environment :: Web Environment
Intended Audience :: Developers
Intended Audience :: Information Technology
Intended Audience :: Science/Research
License :: OSI Approved :: GNU Affero General Public License v3
License :: Free To Use But Restricted
License :: Other/Proprietary License
Programming Language :: Python
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: SQL
Topic :: Database :: Front-Ends
Topic :: Internet :: WWW/HTTP :: WSGI
Topic :: Software Development :: Libraries
""".strip().splitlines() or None
PACKAGE_DIR = {'': 'src'}
INCLUDE_PACKAGE_DATA = True
ZIP_SAFE = False
PACKAGES = """
htsql_sqlite
htsql
sphinxcontrib
htsql_sqlite.core
htsql.ctl
htsql.tweak
htsql.core
sphinxcontrib.texdiag
sphinxcontrib.htsqldoc
htsql_sqlite.core.tr
htsql.tweak.resource
htsql.tweak.inet
htsql.tweak.override
htsql.tweak.cors
htsql.tweak.csrf
htsql.tweak.filedb
htsql.tweak.hello
htsql.tweak.timeout
htsql.tweak.meta
htsql.tweak.django
htsql.tweak.system
htsql.tweak.shell
htsql.tweak.sqlalchemy
htsql.tweak.gateway
htsql.tweak.etl
htsql.tweak.autolimit
htsql.tweak.pool
htsql.core.tr
htsql.core.fmt
htsql.core.syn
htsql.core.cmd
htsql.tweak.meta.slave
htsql.tweak.shell.default
htsql.tweak.etl.tr
htsql.tweak.etl.cmd
htsql.core.tr.fn
""".strip().splitlines()
INSTALL_REQUIRES = """
setuptools
pyyaml
""".strip().splitlines()
CONSOLE_SCRIPTS = """
htsql-ctl = htsql.ctl:main
""".strip().splitlines() or None
HTSQL_ROUTINES = """
default = htsql.ctl.default:DefaultRoutine
help = htsql.ctl.help:HelpRoutine
version = htsql.ctl.version:VersionRoutine
extension = htsql.ctl.extension:ExtensionRoutine
server = htsql.ctl.server:ServerRoutine
shell = htsql.ctl.shell:ShellRoutine
regress = htsql.ctl.regress:RegressRoutine
""".strip().splitlines() or None
HTSQL_ADDONS = """
htsql = htsql.core:HTSQLAddon
engine = htsql.core:EngineAddon
engine.sqlite = htsql_sqlite.core:EngineSQLiteAddon
tweak = htsql.tweak:TweakAddon
tweak.autolimit = htsql.tweak.autolimit:TweakAutolimitAddon
tweak.cors = htsql.tweak.cors:TweakCORSAddon
tweak.csrf = htsql.tweak.csrf:TweakCSRFAddon
tweak.django = htsql.tweak.django:TweakDjangoAddon
tweak.etl = htsql.tweak.etl:TweakETLAddon
tweak.filedb = htsql.tweak.filedb:TweakFileDBAddon
tweak.gateway = htsql.tweak.gateway:TweakGatewayAddon
tweak.hello = htsql.tweak.hello:TweakHelloAddon
tweak.inet = htsql.tweak.inet:TweakINetAddon
tweak.meta = htsql.tweak.meta:TweakMetaAddon
tweak.meta.slave = htsql.tweak.meta.slave:TweakMetaSlaveAddon
tweak.override = htsql.tweak.override:TweakOverrideAddon
tweak.pool = htsql.tweak.pool:TweakPoolAddon
tweak.resource = htsql.tweak.resource:TweakResourceAddon
tweak.shell = htsql.tweak.shell:TweakShellAddon
tweak.shell.default = htsql.tweak.shell.default:TweakShellDefaultAddon
tweak.sqlalchemy = htsql.tweak.sqlalchemy:TweakSQLAlchemyAddon
tweak.system = htsql.tweak.system:TweakSystemAddon
tweak.timeout = htsql.tweak.timeout:TweakTimeoutAddon
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


