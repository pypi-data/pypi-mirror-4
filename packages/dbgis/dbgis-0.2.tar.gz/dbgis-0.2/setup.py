#coding: utf-8
"""python-dbgis

Copyright (c) 2011, Bartosz Fabianowski <bartosz@fabianowski.eu>
Copyright (c) 2012, Bio Eco Forests
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* Neither the name of the author nor the names of its contributors may be used
  to endorse or promote products derived from this software without specific
  prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

$Id: setup.py 5 2011-04-13 16:17:20Z plush $
"""
import distutils.core

version='0.2'

long_description = """\
'python-dbgis is an extension to Psycopg_ and pyspatialite_, respectively a
PostgreSQL_ and SQLite_ database adapter for the Python_ programming language.
python-dbgis support geometry objects used by PostGIS_ and SpatiaLite_ by
translating between their EWKB representation and Python objects.

python-dbgis has been tested with Python 2.7.

python-dbgis is based on PPyGIS_ written by Bartosz Fabianowski
(bartosz@fabianowski.eu). Modifications_ written by Nicolas Évrard
(nicoe@b2ck.com) for Bio Eco Forests.

.. _PPyGIS: http://www.fabianowski.eu/projects/ppygis/
.. _pyspatialite: http://pyspatialite.googlecode.com/
.. _SQLite: http://www.sqlite.org/
.. _Psycopg: http://initd.org/psycopg/
.. _PostgreSQL: http://www.postgresql.org/
.. _Python: http://www.python.org/
.. _PostGIS: http://postgis.refractions.net/
.. _SpatiaLite: http://www.gaia-gis.it/spatialite/'
"""

distutils.core.setup(
    name='dbgis',
    version=version,
    description='PostGIS/SpatiaLite adapter for Psycopg/pyspatialite',
    long_description=long_description,
    maintainer='Bio Eco Forests',
    maintainer_email='pierre-louis.bonicoli@bioecoforests.com',
    url='https://projects.bioecoforests.com/projects/python-dbgis/',
    download_url=
      'https://projects.bioecoforests.com/projects/python-dbgis/files',
    py_modules=['dbgis'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Database :: Front-Ends',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    keywords=['psycopg', 'postgis', 'geometry', 'EWKB'])
