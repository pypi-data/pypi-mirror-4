"""
    pinscher. The core utilities for interacting with pinscher password files.
    Copyright (C) 2012  William Mayor

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    To contact the author please email: mail@williammayor.co.uk
"""
import string
import hashlib
import sqlite3
import random
from Crypto.Cipher import AES


class Database():

    def __init__(self, path, keyfile):
        self.path = path
        self.key, self.iv = Vault.get_key_iv(keyfile)
        with open(path, 'rb') as f:
            self.ciphersql = f.read()

    def __enter__(self):
        self.dbcon = sqlite3.connect(":memory:")
        self.dbcon.executescript(Vault.decrypt(self.key, self.iv, self.ciphersql))
        return self.dbcon.cursor()

    def __exit__(self, type, value, traceback):
        if traceback is None:
            self.dbcon.commit()
        else:
            self.dbcon.rollback()
        lines = list(self.dbcon.iterdump())
        with open(self.path, 'wb') as f:
                f.write(Vault.encrypt(self.key, self.iv, '\n'.join(lines)))
        self.dbcon.close()
        self.dbcon = None


class Vault():

    @staticmethod
    def get_key_iv(keyfile):
        with open(keyfile, 'rb') as f:
            return [s.decode('hex') for s in f.read().split('\n', 1)]

    @staticmethod
    def save_key_iv(keyfile, key, iv):
        with open(keyfile, 'wb') as f:
            f.write("%s\n" % key.encode('hex'))
            f.write(iv.encode('hex'))

    @staticmethod
    def make_key_iv(pin, domain, username):
        """
        Generates the (key, iv) pair required to encrypt text.
        """
        return hashlib.sha256("%s%s%s" % (domain, pin, username)).digest(), hashlib.md5("%s%s%s" % (username, pin, domain)).digest()

    @staticmethod
    def encrypt(key, iv, plaintext):
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        if len(plaintext) % 16 != 0:
            plaintext += ' ' * (16 - len(plaintext) % 16)
        return encryptor.encrypt(plaintext).encode('hex')

    @staticmethod
    def decrypt(key, iv, ciphertext):
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        return encryptor.decrypt(ciphertext.decode('hex')).strip()


def generate(size):
    return ''.join(random.choice(string.digits + string.letters + string.punctuation) for x in range(size))


def delete(database, keyfile, pin, domain, username, password):
    with Database(database, keyfile) as cursor:
        query = "DELETE FROM Credentials WHERE domain = ? AND username = ? AND password = ?"
        key, iv = Vault.make_key_iv(pin, domain, username)
        cursor.execute(query, [domain, username, Vault.encrypt(key, iv, password)])


def update(database, keyfile, pin, domain, username, password):
    with Database(database, keyfile) as cursor:
        query = "UPDATE Credentials SET password = ? WHERE domain = ? AND username = ?"
        key, iv = Vault.make_key_iv(pin, domain, username)
        cursor.execute(query, [Vault.encrypt(key, iv, password), domain, username])


def insert(database, keyfile, pin, domain, username, password):
    with Database(database, keyfile) as cursor:
        query = "INSERT INTO Credentials(domain, username, password) VALUES(?,?,?)"
        key, iv = Vault.make_key_iv(pin, domain, username)
        cursor.execute(query, [domain, username, Vault.encrypt(key, iv, password)])


def password(database, keyfile, pin, domain, username):
    with Database(database, keyfile) as cursor:
        query = "SELECT domain, username, password FROM Credentials WHERE domain = ? AND username = ?"
        cursor.execute(query, [domain, username])
        allresults = cursor.fetchall()
        if len(allresults) == 0:
            query = "SELECT domain, username, password FROM Credentials WHERE domain = ? AND username LIKE (? || '%')"
            cursor.execute(query, [domain, username])
            allresults = cursor.fetchall()
            if len(allresults) == 0:
                query = "SELECT domain, username, password FROM Credentials WHERE domain LIKE (? || '%') AND username LIKE (? || '%')"
                cursor.execute(query, [domain, username])
                allresults = cursor.fetchall()
        if len(allresults) == 1:
            key, iv = Vault.make_key_iv(pin, allresults[0][0], allresults[0][1])
            return [(allresults[0][0], allresults[0][1], Vault.decrypt(key, iv, allresults[0][2]))]
        else:
            return [(r[0], r[1], None) for r in allresults]


def users(database, keyfile, domain):
    with Database(database, keyfile) as cursor:
        query = "SELECT domain, username FROM Credentials WHERE domain LIKE (? || '%')"
        cursor.execute(query, [domain])
        return cursor.fetchall()


def domains(database, keyfile):
    with Database(database, keyfile) as cursor:
        query = "SELECT DISTINCT domain FROM Credentials"
        cursor.execute(query)
        return [d[0] for d in cursor.fetchall()]
