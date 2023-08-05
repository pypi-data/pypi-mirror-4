# -*- coding: utf-8 -*-
"""Test dbtoyaml and yamltodb using autodoc schema

See http://cvs.pgfoundry.org/cgi-bin/cvsweb.cgi/~checkout~/autodoc/autodoc/
regressdatabase.sql?rev=1.2
"""
import os
import subprocess
import tempfile
import glob
import unittest

from pyrseas.testutils import PostgresDb
from pyrseas.testutils import TEST_DBNAME, TEST_USER, TEST_HOST, TEST_PORT

TEST_DBNAME_SRC = 'pyrseas_testdb_src'
EMPTY_YAML = """\
schema public:
  description: standard public schema
  owner: postgres

"""


class AutodocTestCase(unittest.TestCase):

    def setUp(self):
        self.srcdb = PostgresDb(TEST_DBNAME_SRC, TEST_USER, TEST_HOST,
                                TEST_PORT)
        self.srcdb.connect()
        self.srcdb.clear()
        self.db = PostgresDb(TEST_DBNAME, TEST_USER, TEST_HOST, TEST_PORT)
        self.db.connect()
        self.db.clear()
        self.wd = os.path.abspath(os.path.dirname(__file__))
        progdir = os.path.abspath(os.path.join(self.wd, '../../pyrseas'))
        self.dbtoyaml = os.path.join(progdir, 'dbtoyaml.py')
        self.yamltodb = os.path.join(progdir, 'yamltodb.py')
        self.tmpdir = tempfile.gettempdir()

    def tearDown(self):
        for tfile in glob.glob(os.path.join(self.tmpdir, 'autodoc*')):
            os.remove(tfile)

    def test_autodoc(self):
        # Create the source schema
        schfile = os.path.join(self.wd, 'autodoc-schema.sql')
        lines = []
        with open(schfile, 'r') as fd:
            lines = [line.strip() for line in fd if line != '\n' and
                     not line.startswith('--')]
        self.srcdb.execute(' '.join(lines))

        # Run pg_dump against TEST_DBNAME_SRC to create autodoc-src.dump
        srcdump = os.path.join(self.tmpdir, 'autodoc-src.dump')
        subprocess.call(['pg_dump', '-s', '-f', srcdump, TEST_DBNAME_SRC])

        # Create source YAML file
        srcyaml = os.path.join(self.tmpdir, 'autodoc-src.yaml')
        subprocess.call([self.dbtoyaml, '-o', srcyaml, TEST_DBNAME_SRC])

        # Run pg_dump against TEST_DBNAME to create empty.dump
        emptydump = os.path.join(self.tmpdir, 'empty.dump')
        subprocess.call(['pg_dump', '-s', '-f', emptydump, TEST_DBNAME])

        # Generate target SQL
        targsql = os.path.join(self.tmpdir, 'autodoc.sql')
        subprocess.call([self.yamltodb, '-u', '-o', targsql, TEST_DBNAME,
                         srcyaml])

        # Run pg_dump against TEST_DBNAME to create autodoc.dump
        targdump = os.path.join(self.tmpdir, 'autodoc.dump')
        subprocess.call(['pg_dump', '-s', '-f', targdump, TEST_DBNAME])

        # Create target YAML file
        targyaml = os.path.join(self.tmpdir, 'autodoc.yaml')
        subprocess.call([self.dbtoyaml, '-o', targyaml, TEST_DBNAME])

        # diff autodoc-src.dump against autodoc.dump
        self.assertEqual(open(srcdump).readlines(), open(targdump).readlines())
        # diff autodoc-src.yaml against autodoc.yaml
        self.assertEqual(open(srcyaml).readlines(), open(targyaml).readlines())

        # Undo the changes
        open(srcyaml, 'w').writelines(EMPTY_YAML)
        subprocess.call([self.yamltodb, '-u', '-o', targsql, TEST_DBNAME,
                         srcyaml])

        # Run pg_dump against TEST_DBNAME to create autodoc.dump
        subprocess.call(['pg_dump', '-s', '-f', targdump, TEST_DBNAME])

        # Create target YAML file
        subprocess.call([self.dbtoyaml, '-o', targyaml, TEST_DBNAME])

        # diff empty.dump autodoc.dump
        self.assertEqual(open(emptydump).readlines(),
                         open(targdump).readlines())
        # diff autodoc-src.yaml against autodoc.yaml
        self.assertEqual(open(srcyaml).readlines(), open(targyaml).readlines())


def suite():
    tests = unittest.TestLoader().loadTestsFromTestCase(AutodocTestCase)
    return tests

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
