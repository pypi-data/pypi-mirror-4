import unittest
import tempfile
import os
from pinscher import pinscher as core


def walk_up(bottom):
    bottom = os.path.realpath(bottom)

    try:
        names = os.listdir(bottom)
    except Exception:
        return

    dirs, nondirs = [], []
    for name in names:
        if os.path.isdir(os.path.join(bottom, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    yield bottom, dirs, nondirs

    new_path = os.path.realpath(os.path.join(bottom, '..'))
    if new_path == bottom:
        return

    for x in walk_up(new_path):
        yield x


def find_schema():
    for current, dirs, files in walk_up(os.path.dirname(os.path.abspath(__file__))):
        if 'pinscher.schema' in files:
            path = os.path.join(current, 'pinscher.schema')
            if not os.path.islink(path):
                return path


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.pin = 1234
        self.domain = 'domain'
        self.username = 'username'
        self.password = 'password'
        self.key, self.iv = core.Vault.make_key_iv(self.pin, self.domain, self.username)

        tempkeyfile = tempfile.NamedTemporaryFile()
        core.Vault.save_key_iv(tempkeyfile.name, self.key, self.iv)

        tempdb = tempfile.NamedTemporaryFile()
        with open(find_schema(), "r") as f:
            schema = f.read()
            with core.Database(tempdb.name, tempkeyfile.name) as cursor:
                cursor.executescript(schema)

        self.db = tempdb
        self.keyfile = tempkeyfile

    def tearDown(self):
        self.db.close()
        self.keyfile.close()

    def test_load_blank_file(self):
        with core.Database(self.db.name, self.keyfile.name):
            #loaded from blank file
            pass

    def test_load_empty_database(self):
        with core.Database(self.db.name, self.keyfile.name):
            #loaded from blank file
            pass
        #closed and saved
        with core.Database(self.db.name, self.keyfile.name):
            #loaded from minimal file
            pass

    def test_insert(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, self.domain, self.username, self.password)
        self.assertEquals([(self.domain, self.username, self.password)], core.password(self.db.name, self.keyfile.name, self.pin, self.domain, self.username))

    def test_update(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, self.domain, self.username, self.password)
        core.update(self.db.name, self.keyfile.name, self.pin, self.domain, self.username, 'notpassword')
        self.assertEquals([(self.domain, self.username, 'notpassword')], core.password(self.db.name, self.keyfile.name, self.pin, self.domain, self.username))

    def test_delete(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, self.domain, self.username, self.password)
        core.delete(self.db.name, self.keyfile.name, self.pin, self.domain, self.username, self.password)
        self.assertEquals([], core.password(self.db.name, self.keyfile.name, self.pin, self.domain, self.username))
