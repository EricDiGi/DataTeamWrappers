import unittest
import os, sys
import json
import envy

test_profile_json = """{
    "name": "test profile",
    "age": "123",
    "car": "Ford"
}"""

test_profile_env= """
NAME=test profile
AGE=123
CAR=Ford
"""

class TestEnvy(unittest.TestCase):
    def setUp(self):
        self.json_file = "test_profile.json"
        self.env_file = "test_profile.env"
        with open(self.json_file, "w") as f:
            f.write(test_profile_json)
        with open(self.env_file, "w") as f:
            f.write(test_profile_env)
    
    def tearDown(self):
        os.remove(self.json_file)
        os.remove(self.env_file)

    def test_json_to_env(self):
        self.assertEqual(
            envy.json(self.json_file, default=False), None,
            "envy.json() should return None when loading as an ENV"
        )
        self.assertEqual(
            os.environ['Name'], 'test profile',
            "Json could not be loaded as an ENV"
        )
    def test_json_to_json(self):
        self.assertEqual(
            envy.json(self.json_file, default=True), json.loads(test_profile_json),
            "Loaded dictionary doesn't match original when loading JSON as JSON"
        )
    def test_env_to_json(self):
        self.assertEqual(
            envy.env(self.env_file, default=False, flags=[envy.SNAKE_CASE]), json.loads(test_profile_json),
            "Loaded dictionary doesn't match original when loading ENV as JSON"
        )
    def test_env_to_env(self):
        self.assertEqual(
            envy.env(self.env_file, default=True), None,
            "envy.env() should return None when loading as an ENV"
        )
        self.assertEqual(
            os.environ['Name'], 'test profile',
            "Env could not be loaded as an ENV"
        )

    def test_arbiter_to_json(self):
        self.assertEquals(
            envy.arbiter(self.json_file, default=envy.is_json(self.json_file),flags=[envy.SNAKE_CASE]),
            json.loads(test_profile_json),
            "Loaded file doesn't match original when loading JSON as JSON using Arbiter"
        )
        self.assertEquals(
            envy.arbiter(self.env_file, default=envy.is_json(self.env_file),flags=[envy.SNAKE_CASE]),
            json.loads(test_profile_json),
            "Loaded file doesn't match original when loading ENV as JSON using Arbiter"
        )

    def test_arbiter_to_env(self):
        self.assertEquals(
            envy.arbiter(self.json_file, default=envy.is_env(self.json_file),flags=[envy.SNAKE_CASE]),
            None,
            "envy.arbiter() should return None when loading as an ENV using Arbiter"
        )
        self.assertEquals( os.environ['Name'], 'test profile', "File could not be loaded as an ENV using Arbiter" )
        self.assertEquals(
            envy.arbiter(self.env_file, default=envy.is_env(self.env_file),flags=[envy.SNAKE_CASE]),
            None,
            "envy.arbiter() should return None when loading as an ENV using Arbiter"
        )
        self.assertEquals( os.environ['Name'], 'test profile', "File could not be loaded as an ENV using Arbiter" )