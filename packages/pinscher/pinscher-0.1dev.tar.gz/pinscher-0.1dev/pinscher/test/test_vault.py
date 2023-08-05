import unittest
import tempfile
from pinscher.pinscher import Vault


class TestVault(unittest.TestCase):

    def setUp(self):
        self.key, self.iv = Vault.make_key_iv(1234, 'domain', 'username')

    def test_load_and_save(self):
        with tempfile.NamedTemporaryFile() as tempf:
            Vault.save_key_iv(tempf.name, self.key, self.iv)
            self.assertEqual([self.key, self.iv], Vault.get_key_iv(tempf.name))

    def test_encrypt_decrypt(self):
        plaintext = 'test'
        ciphertext = Vault.encrypt(self.key, self.iv, plaintext)
        self.assertEqual(plaintext, Vault.decrypt(self.key, self.iv, ciphertext))
