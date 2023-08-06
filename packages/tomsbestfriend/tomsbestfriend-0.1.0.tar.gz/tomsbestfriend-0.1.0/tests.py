from datetime import datetime
from glob import iglob as glob
import json
import os
import re

try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

import parsley

import tomsbestfriend


THIS_DIR = os.path.dirname(__file__)
TESTS_DIR = os.path.join(THIS_DIR, "toml-test", "tests")


def load_tests(tests_dir=TESTS_DIR):
    """
    Load the TOML Suite tests from the given directory.

    """

    def valid(toml, output):
        def test(self):
            self.assertEqual(tomsbestfriend.loads(toml), output)
        return test


    def invalid(toml, name):
        def test(self):
            exception, msg = self.errors.get(name, (parsley.ParseError, None))
            with self.assertRaises(exception) as e:
                tomsbestfriend.loads(toml)
            if msg is not None:
                self.assertEqual(str(e.exception).replace("u'", "'"), msg)
        return test


    def reconvert(thing):
        """
        Properly reconvert the values in the output.

        """

        types = {
            "bool" : {"true" : True, "false" : False}.get,
            "datetime" : lambda d : datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ"),
            "float" : float,
            "integer" : int,
        }

        if "type" in thing:
            return types.get(thing["type"], lambda i : i)(thing["value"])
        return thing


    def add_test_methods(test_class):
        for path in glob(os.path.join(tests_dir, "*", "*.toml")):
            name = re.sub(r"[\W ]+", "_", os.path.basename(path)[:-5])
            expect = os.path.basename(os.path.dirname(path))
            test_name = "_".join(("test", expect, name))

            with open(path) as test_file:
                if expect == "valid":
                    with open(os.path.splitext(path)[0] + ".json") as out_file:
                        output = json.load(out_file, object_hook=reconvert)
                        test = valid(test_file.read(), output)
                elif expect == "invalid":
                        test = invalid(test_file.read(), test_name)
                else:
                    raise ValueError("Didn't expect: %r" % (expect,))

            test.__name__ = test_name
            setattr(test_class, test_name, test)

        return test_class
    return add_test_methods


@load_tests()
class TestTOMLSuite(TestCase):
    errors = {
        "test_invalid_duplicate_keys" : (
            tomsbestfriend.Duplicated,
            "'dupe' already appears in the document.",
        ),
        "test_invalid_duplicate_keygroups" : (
            tomsbestfriend.Duplicated, "'a' already appears in the document.",
        ),
        "test_invalid_duplicate_key_keygroup" : (
            tomsbestfriend.Duplicated, "'type' already appears in 'fruit'.",
        ),
        "test_invalid_array_mixed_types_arrays_and_ints" : (
            TypeError, "[1, ['Arrays are not integers.']] is not homogeneous.",
        ),
        "test_invalid_array_mixed_types_ints_and_floats" : (
            TypeError, "[1, 1.0] is not homogeneous.",
        ),
        "test_invalid_array_mixed_types_strings_and_ints" : (
            TypeError, "['hi', 42] is not homogeneous.",
        ),
    }
