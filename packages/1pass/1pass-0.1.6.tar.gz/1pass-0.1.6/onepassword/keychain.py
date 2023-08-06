import json
import os

from onepassword.encryption_key import EncryptionKey


class Keychain(object):
    def __init__(self, path):
        self._path = os.path.expanduser(path)
        self._load_encryption_keys()
        self._load_item_list()
        self._locked = True

    def unlock(self, password):
        unlocker = lambda key: key.unlock(password)
        unlock_results = map(unlocker, self._encryption_keys.values())
        result = reduce(lambda x, y: x and y, unlock_results)
        self._locked = not result
        return result

    def item(self, name):
        if name in self._items:
            item = self._items[name]
            key = self._encryption_keys[item.key_identifier]
            item.decrypt_with(key)
            return item
        else:
            return None

    @property
    def locked(self):
        return self._locked

    def _load_encryption_keys(self):
        path = os.path.join(self._path, "data", "default", "encryptionKeys.js")
        with open(path, "r") as f:
            key_data = json.load(f)

        self._encryption_keys = {}
        for key_definition in key_data["list"]:
            key = EncryptionKey(**key_definition)
            self._encryption_keys[key.identifier] = key

    def _load_item_list(self):
        path = os.path.join(self._path, "data", "default", "contents.js")
        with open(path, "r") as f:
            item_list = json.load(f)

        self._items = {}
        for item_definition in item_list:
            item = KeychainItem.build(item_definition, self._path)
            self._items[item.name] = item


class KeychainItem(object):
    @classmethod
    def build(cls, row, path):
        identifier = row[0]
        type = row[1]
        name = row[2]
        if type == "webforms.WebForm":
            return WebFormKeychainItem(identifier, name, path)
        elif type == "passwords.Password":
            return PasswordKeychainItem(identifier, name, path)
        else:
            return KeychainItem(identifier, name, path)

    def __init__(self, identifier, name, path):
        self.identifier = identifier
        self.name = name
        self.password = None
        self._path = path

    @property
    def key_identifier(self):
        return self._lazily_load("_key_identifier")

    def decrypt_with(self, key):
        encrypted_json = self._lazily_load("_encrypted_json")
        decrypted_json = key.decrypt(self._encrypted_json)
        self._data = json.loads(decrypted_json)
        self.password = self._find_password()

    def _find_password(self):
        raise Exception("Cannot extract a password from this type of"
                        " keychain item")

    def _lazily_load(self, attr):
        if not hasattr(self, attr):
            self._read_data_file()
        return getattr(self, attr)

    def _read_data_file(self):
        filename = "%s.1password" % self.identifier
        path = os.path.join(self._path, "data", "default", filename)
        with open(path, "r") as f:
            item_data = json.load(f)

        self._key_identifier = item_data["keyID"]
        self._encrypted_json = item_data["encrypted"]


class WebFormKeychainItem(KeychainItem):
    def _find_password(self):
        for field in self._data["fields"]:
            if field.get("designation") == "password" or \
               field.get("name") == "Password":
                return field["value"]


class PasswordKeychainItem(KeychainItem):
    def _find_password(self):
        return self._data["password"]
