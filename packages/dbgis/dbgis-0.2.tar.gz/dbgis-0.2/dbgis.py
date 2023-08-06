"""dbgis

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

"""
import binascii
import cStringIO
import struct
from itertools import izip_longest


class _EWKBReader(object):

    def __init__(self, stream):
        self.stream = stream

    def child_reader(self):
        return _EWKBReader(self.stream)

    def read_geometry(self):
        byte_order = self.stream.read(1)
        if byte_order == '\x00':
            self._endianness = '>'
        elif byte_order == '\x01':
            self._endianness = '<'
        else:
            raise Exception('invalid EWKB encoding')

        type = self.read_int()
        self.has_z = bool(type & 0x80000000)
        self.has_m = bool(type & 0x40000000)
        srid = self.read_int() if bool(type & 0x20000000) else None
        type &= 0x1fffffff

        if type == 1:
            return Point._read_ewkb_body(self, srid)
        elif type == 2:
            return LineString._read_ewkb_body(self, srid)
        elif type == 3:
            return Polygon._read_ewkb_body(self, srid)
        elif type == 4:
            return MultiPoint._read_ewkb_body(self, srid)
        elif type == 5:
            return MultiLineString._read_ewkb_body(self, srid)
        elif type == 6:
            return MultiPolygon._read_ewkb_body(self, srid)
        elif type == 7:
            return GeometryCollection._read_ewkb_body(self, srid)
        else:
            raise Exception('unsupported geometry type {0}'.format(type))

    def read_int(self):
        return struct.unpack(self._endianness + 'I', self.stream.read(4))[0]

    def read_double(self):
        return struct.unpack(self._endianness + 'd', self.stream.read(8))[0]


class _EWKBWriter(object):

    def __init__(self, geometry, stream=None):
        self.stream = stream or cStringIO.StringIO()
        if isinstance(geometry, Point):
            type = 1
        elif isinstance(geometry, LineString):
            type = 2
        elif isinstance(geometry, Polygon):
            type = 3
        elif isinstance(geometry, MultiPoint):
            type = 4
        elif isinstance(geometry, MultiLineString):
            type = 5
        elif isinstance(geometry, MultiPolygon):
            type = 6
        elif isinstance(geometry, GeometryCollection):
            type = 7
        else:
            raise Exception('unsupported geometry class <{0}>'
                    .format(geometry.__class__.__name__))

        self.stream.write('\x01')
        self.write_int(
                type |
                (0x80000000 if geometry.has_z else 0) |
                (0x40000000 if geometry.has_m else 0) |
                (0x20000000 if geometry.has_srid else 0))
        if geometry.has_srid:
            self.write_int(geometry.srid)

    def child_writer(self, geometry):
        return _EWKBWriter(geometry, self.stream)

    def write_int(self, value):
        self.stream.write(struct.pack('<I', value))

    def write_double(self, value):
        self.stream.write(struct.pack('<d', value))


class _SQLiteBlobReader(object):

    def __init__(self, stream):
        if isinstance(stream, (str, buffer)):
            stream = cStringIO.StringIO(stream)
        self.stream = stream

    def read_geometry(self):
        self.stream.read(1)
        byte_order = self.stream.read(1)
        if byte_order == '\x00':
            self.endianness = '>'
        elif byte_order == '\x01':
            self.endianness = '<'
        else:
            raise ValueError('Incorrect endianness value')
        srid = self.read_int()
        self.stream.read(32)
        assert self.stream.read(1) == '\x7C'
        geom_type = self.read_int()

        if geom_type == 1:
            geom = Point._read_sqlite_body(self, srid)
        else:
            raise ValueError('Unsupported geometry type')

        assert self.stream.read(1) == '\xFE'
        return geom

    def read_int(self):
        return struct.unpack(self.endianness + 'I', self.stream.read(4))[0]

    def read_double(self):
        return struct.unpack(self.endianness + 'd', self.stream.read(8))[0]


class Geometry(object):

    _type = 'Geometry'

    @property
    def has_z(self):
        return False

    @property
    def has_m(self):
        return False

    @property
    def wkt(self):
        wkt = self._type + ' '
        if self.has_z:
            wkt += 'z'
        if self.has_m:
            wkt += 'm'
        if self.has_z or self.has_m:
            wkt += ' '
        wkt += self.untagged_wkt
        return wkt.upper()

    @property
    def has_srid(self):
        return self.srid is not None

    @staticmethod
    def read_ewkb(value, cursor=None):
        return _EWKBReader(cStringIO.StringIO(binascii.a2b_hex(value))) \
                .read_geometry() if value else None

    @staticmethod
    def _read_ewkb(reader):
        return _EWKBReader(reader.stream).read_geometry()

    @staticmethod
    def read_sqlite_blob(value, cursor=None):
        return _SQLiteBlobReader(value).read_geometry() if value else None

    def write_ewkb(self):
        writer = _EWKBWriter(self)
        self._write_ewkb_body(writer)
        return binascii.b2a_hex(writer.stream.getvalue())

    def getquoted(self):
        return '\'' + self.write_ewkb() + '\''

    def _write_ewkb(self, writer):
        self._write_ewkb_body(writer.child_writer(self))

    def _str_srid(self):
        return ', SRID: {0}'.format(self.srid) if self.has_srid else ''


class Point(Geometry):

    _type = 'Point'

    def __init__(self, x, y, z=None, m=None, srid=None):
        self.x = x
        self.y = y
        self.z = z
        self.m = m
        self.srid = srid

    @property
    def has_z(self):
        return self.z is not None

    @property
    def has_m(self):
        return self.m is not None

    @property
    def untagged_wkt(self):
        return '(' + self.coordinates + ')'

    @property
    def coordinates(self):
        uwkt = '%s %s' % (self.x, self.y)
        if self.has_z:
            uwkt += ' %s' % self.z
        if self.has_m:
            uwkt += ' %s' % self.m
        return uwkt

    @classmethod
    def _read_ewkb_body(cls, reader, srid=None):
        return cls(
                reader.read_double(),
                reader.read_double(),
                reader.read_double() if reader.has_z else None,
                reader.read_double() if reader.has_m else None,
                srid)

    def _write_ewkb_body(self, writer):
        writer.write_double(self.x)
        writer.write_double(self.y)
        if self.has_z:
            writer.write_double(self.z)
        if self.has_m:
            writer.write_double(self.m)

    @classmethod
    def _read_sqlite_body(cls, reader, srid=None):
        return cls(reader.read_double(), reader.read_double(), srid=srid)

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        for attribute in ('srid', 'x', 'y', 'z', 'm'):
            if getattr(self, attribute) != getattr(other, attribute):
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return 'Point(X: {0}, Y: {1}'.format(self.x, self.y) + \
                (', Z: {0}'.format(self.z) if self.has_z else '') + \
                (', M: {0}'.format(self.m) if self.has_m else '') + \
                self._str_srid() + ')'


class LineString(Geometry):

    _type = 'LineString'

    def __init__(self, points, srid=None):
        self.points = list(points)
        self.srid = srid

    @property
    def has_z(self):
        return self.points[0].has_z

    @property
    def has_m(self):
        return self.points[0].has_m

    @property
    def untagged_wkt(self):
        return '(' + ', '.join(p.coordinates for p in self.points) + ')'

    @classmethod
    def _read_ewkb_body(cls, reader, srid=None):
        return cls([Point._read_ewkb_body(reader) for index in
                range(reader.read_int())], srid)

    def _write_ewkb_body(self, writer):
        writer.write_int(len(self.points))
        for point in self.points:
            if isinstance(point, Point):
                point._write_ewkb_body(writer)
            else:
                raise Exception('invalid geometry')

    def __eq__(self, other):
        if not isinstance(other, LineString):
            return False
        for point_self, point_other in izip_longest(self.points, other.points):
            if point_self != point_other:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return 'LineString(' + ', '.join([str(point) for point in
                self.points]) + self._str_srid() + ')'


class Polygon(Geometry):

    _type = 'Polygon'

    def __init__(self, rings, srid=None):
        self.rings = list(rings)
        self.srid = srid

    @property
    def has_z(self):
        return self.rings[0].has_z

    @property
    def has_m(self):
        return self.rings[0].has_m

    @property
    def untagged_wkt(self):
        return '(' + ', '.join(r.untagged_wkt for r in self.rings) + ')'

    @classmethod
    def _read_ewkb_body(cls, reader, srid=None):
        return cls([LineString._read_ewkb_body(reader) for index in
                range(reader.read_int())], srid)

    def _write_ewkb_body(self, writer):
        writer.write_int(len(self.rings))
        for ring in self.rings:
            if isinstance(ring, LineString):
                ring._write_ewkb_body(writer)
            else:
                raise Exception('invalid geometry')

    def __eq__(self, other):
        if not isinstance(other, Polygon):
            return False
        for ring_self, ring_other in izip_longest(self.rings, other.rings):
            if ring_self != ring_other:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return 'Polygon(' + ', '.join([str(ring) for ring in self.rings]) + \
                self._str_srid() + ')'

    def __iter__(self):
        return iter(self.rings)


class GeometryCollection(Geometry):

    _type = 'GeometryCollection'

    def __init__(self, geometries, srid=None):
        self.geometries = list(geometries)
        self.srid = srid

    @property
    def has_z(self):
        return self.geometries[0].has_z

    @property
    def has_m(self):
        return self.geometries[0].has_m

    @property
    def untagged_wkt(self):
        return '(' + ', '.join(g.untagged_wkt for g in self.geometries) + ')'

    @classmethod
    def _read_ewkb_body(cls, reader, srid=None):
        return cls([reader.child_reader().read_geometry() for index in
                range(reader.read_int())], srid)

    def _write_ewkb_body(self, writer):
        writer.write_int(len(self.geometries))
        for geometry in self.geometries:
            geometry._write_ewkb(writer)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        for geo1, geo2 in izip_longest(self, other):
            if geo1 != geo2:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return 'GeometryCollection(' + ', '.join([str(geometry) for geometry in
                self.geometries]) + self._str_srid() + ')'

    def __iter__(self):
        return iter(self.geometries)


class MultiPoint(GeometryCollection):

    _type = 'MultiPoint'

    def __init__(self, points, srid=None):
        self.points = list(points)
        self.srid = srid

    @property
    def has_z(self):
        return self.points[0].has_z

    @property
    def has_m(self):
        return self.points[0].has_m

    @property
    def untagged_wkt(self):
        return '(' + ', '.join(p.untagged_wkt for p in self.points) + ')'

    @classmethod
    def _read_ewkb_body(cls, reader, srid=None):
        points = []
        for index in range(reader.read_int()):
            child = reader.child_reader().read_geometry()
            if not isinstance(child, Point):
                raise Exception('invalid geometry')
            points.append(child)
        return cls(points, srid)

    def _write_ewkb_body(self, writer):
        writer.write_int(len(self.points))
        for point in self.points:
            if isinstance(point, Point):
                point._write_ewkb(writer)
            else:
                raise Exception('invalid geometry')

    def __str__(self):
        return 'MultiPoint(' + ', '.join([str(point) for point in
                self.points]) + self._str_srid() + ')'

    def __iter__(self):
        return iter(self.points)


class MultiLineString(GeometryCollection):

    _type = 'MultiLineString'

    def __init__(self, lines, srid=None):
        self.lines = list(lines)
        self.srid = srid

    @property
    def has_z(self):
        return self.lines[0].has_z

    @property
    def has_m(self):
        return self.lines[0].has_m

    @property
    def untagged_wkt(self):
        return '(' + ', '.join(l.untagged_wkt for l in self.lines) + ')'

    @classmethod
    def _read_ewkb_body(cls, reader, srid=None):
        lines = []
        for index in range(reader.read_int()):
            child = reader.child_reader().read_geometry()
            if not isinstance(child, LineString):
                raise Exception('invalid geometry')
            lines.append(child)
        return cls(lines, srid)

    def _write_ewkb_body(self, writer):
        writer.write_int(len(self.lines))
        for line in self.lines:
            if isinstance(line, LineString):
                line._write_ewkb(writer)
            else:
                raise Exception('invalid geometry')

    def __str__(self):
        return 'MultiLineString(' + ', '.join([str(line) for line in
                self.lines]) + self._str_srid() + ')'

    def __iter__(self):
        return iter(self.lines)


class MultiPolygon(GeometryCollection):

    _type = 'MultiPolygon'

    def __init__(self, polygons, srid=None):
        self.polygons = list(polygons)
        self.srid = srid

    @property
    def has_z(self):
        return self.polygons[0].has_z

    @property
    def has_m(self):
        return self.polygons[0].has_m

    @property
    def untagged_wkt(self):
        return '(' + ', '.join(p.untagged_wkt for p in self.polygons) + ')'

    @classmethod
    def _read_ewkb_body(cls, reader, srid=None):
        polygons = []
        for index in range(reader.read_int()):
            child = reader.child_reader().read_geometry()
            if not isinstance(child, Polygon):
                raise Exception('invalid geometry')
            polygons.append(child)
        return cls(polygons, srid)

    def _write_ewkb_body(self, writer):
        writer.write_int(len(self.polygons))
        for polygon in self.polygons:
            if isinstance(polygon, Polygon):
                polygon._write_ewkb(writer)
            else:
                raise Exception('invalid geometry')

    def __str__(self):
        return 'MultiPolygon(' + ', '.join([str(polygon) for polygon in
                self.polygons]) + self._str_srid() + ')'

    def __iter__(self):
        return iter(self.polygons)


def register_psycopg(connection, scope=None):
    from psycopg2.extensions import (new_type, register_type, register_adapter,
        AsIs)

    cursor = connection.cursor()
    cursor.execute('SELECT pg_type.oid '
        'FROM pg_type '
        'JOIN pg_namespace '
            'ON typnamespace = pg_namespace.oid '
        'WHERE typname = %(typename)s ',
        {'typename': 'geometry'})

    if cursor.rowcount == 0:
        raise Exception("'%s' Postgis is not enabled", connection.dsn)

    geometry_oid, = cursor.fetchone()
    cursor.close()
    GEOMETRY = new_type((geometry_oid,), "GEOMETRY", Geometry.read_ewkb)
    register_type(GEOMETRY, scope)
    for klass in (Point, LineString, Polygon, MultiPoint, MultiLineString,
            MultiPolygon, GeometryCollection):
        register_adapter(klass, lambda o: AsIs("'%s'" % o.write_ewkb()))

def register_spatialite():
    from pyspatialite.dbapi2 import register_converter
    register_converter('POINT', Point.read_sqlite_blob)
