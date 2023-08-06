import unittest
import rapidjson


class TestDecodeSimple(unittest.TestCase):

    def test_integer(self):
        text = "12"
        ret = rapidjson.loads(text)
        self.assertEqual(ret, 12)

    def test_negative_integer(self):
        text = "-12"
        ret = rapidjson.loads(text)
        self.assertEqual(ret, -12)

    def test_float(self):
        text = "12.3"
        ret = rapidjson.loads(text)
        self.assertEqual(ret, 12.3)

    def test_negative_float(self):
        text = "-12.3"
        ret = rapidjson.loads(text)
        self.assertEqual(ret, -12.3)

    def test_string(self):
        text = "\"hello world\""
        ret = rapidjson.loads(text)
        self.assertEqual(ret, "hello world")

    def test_true(self):
        text = "true"
        ret = rapidjson.loads(text)
        self.assertEqual(ret, True)

    def test_false(self):
        text = "false"
        ret = rapidjson.loads(text)
        self.assertEqual(ret, False)

    def test_none(self):
        text = "null"
        ret = rapidjson.loads(text)
        self.assertEqual(ret, None)

    def test_list_size_one(self):
        text = "[null]"
        ret = rapidjson.loads(text)
        self.assertEqual(ret, [None])

    def test_list_size_two(self):
        text = "[false, -50.3]"
        ret = rapidjson.loads(text)
        self.assertEqual(ret, [False, -50.3])

    def test_dict_size_one(self):
        text = """{"20":null}"""
        ret = rapidjson.loads(text)
        self.assertEqual(ret, {'20': None})

    def test_dict_size_two(self):
        text = """{"hoge":null, "huga":134}"""
        ret = rapidjson.loads(text)
        self.assertEqual(ret, {"hoge": None, "huga": 134})


class TestDecodeComplex(unittest.TestCase):

    def test_list_in_dict(self):
        text = """{"test": [1, "hello"]}"""
        ret = rapidjson.loads(text)
        self.assertEqual(ret, {"test": [1, "hello"]})

    def test_dict_in_dict(self):
        text = """{"test": {"hello": "world"}}"""
        ret = rapidjson.loads(text)
        self.assertEqual(ret, {"test": {"hello": "world"}})


class TestEncodeSimple(unittest.TestCase):

    def test_integer(self):
        jsonobj = 1
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, "1")

    def test_negative_integer(self):
        jsonobj = -100
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, "-100")

    def test_float(self):
        jsonobj = 12.3
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, "12.3")

    def test_negative_float(self):
        jsonobj = -12.3
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, "-12.3")

    def test_string(self):
        jsonobj = "hello world"
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, "\"hello world\"")

    def test_true(self):
        jsonobj = True
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, "true")

    def test_false(self):
        jsonobj = False
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, "false")

    def test_none(self):
        jsonobj = None
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, "null")

    def test_list_size_one(self):
        jsonobj = [None, ]
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, "[null]")

    def test_list_size_two(self):
        jsonobj = [False, -50.3]
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, "[false,-50.3]")

    def test_dict_size_one(self):
        jsonobj = {'20': None}
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, """{"20":null}""")

    def test_dict_size_two(self):
        jsonobj = {"hoge": None, "huga": 134}
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, """{"huga":134,"hoge":null}""")


class TestEncodeComplex(unittest.TestCase):

    def test_list_in_dict(self):
        jsonobj = {"test": [1, "hello"]}
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, """{"test":[1,"hello"]}""")

    def test_dict_in_dict(self):
        jsonobj = {"test": {"hello": "world"}}
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, """{"test":{"hello":"world"}}""")

    def test_dict_in_dict_and_list(self):
        jsonobj = {"test": {"hello": ["world", "!!"]}}
        ret = rapidjson.dumps(jsonobj)
        self.assertEqual(ret, """{"test":{"hello":["world","!!"]}}""")
