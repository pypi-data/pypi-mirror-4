import codecs
import runtime
import formast
import nose.tools
import sys
import os.path
import unittest

unittest.TestCase.maxDiff = None

def open_text(filename):
    # swig expects a str
    if sys.version_info.major < 3:
        return open(filename, "rb")
    else:
        return codecs.open(filename, "rb", "ascii")

# returns the actual module, so we can use it in further tests
def get_runtime():
    top = formast.Top()
    with open_text("codegen/integers.xml") as stream:
        formast.XmlParser().parse_string(stream.read(), top)
    return runtime.RuntimeModule(top)

def test_runtime_top():
    mod = get_runtime()
    nose.tools.assert_in("IntegerData", dir(mod))

def test_runtime_class():
    mod = get_runtime()
    data = mod.IntegerData()
    nose.tools.assert_in("version", dir(data))

def test_ver0_1():
    mod = get_runtime()
    data = mod.IntegerData()
    with open("test_ver0_1.integers", "rb") as stream:
        data.read(stream)
        eof_check = stream.read(1)
    nose.tools.assert_equal(eof_check, b'')
    nose.tools.assert_equal(data.version, 0)
    nose.tools.assert_equal(data.has_integers, 1)
    nose.tools.assert_equal(data.has_integers_2, 0)
    nose.tools.assert_equal(data.num_integers, 3)
    nose.tools.assert_list_equal(data.integers, [3, 1, 4])
    nose.tools.assert_equal(data.num_integers_2, 0)
    nose.tools.assert_list_equal(data.integers_2, [])

def test_ver2_1():
    mod = get_runtime()
    data = mod.IntegerData()
    with open("test_ver2_1.integers", "rb") as stream:
        data.read(stream)
        eof_check = stream.read(1)
    nose.tools.assert_equal(eof_check, b'')
    nose.tools.assert_equal(data.version, 2)
    nose.tools.assert_equal(data.has_integers, 1)
    nose.tools.assert_equal(data.has_integers_2, 1)
    nose.tools.assert_equal(data.num_integers, 3)
    nose.tools.assert_list_equal(data.integers, [3, 1, 4])
    nose.tools.assert_equal(data.num_integers_2, 5)
    nose.tools.assert_list_equal(data.integers_2, [2, 7, 1, 8, 2])
