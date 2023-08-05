import unittest

from cstypo import parser


class TestCoding(unittest.TestCase):
    def parse_file(self, name):
        content = open(name).read()
        inst = parser.TxtParser(content)
        parsed = inst.parse()
        print type(parsed)
        right = open(name + '.parsed').read().encode('utf8')
        print type(right)
        #self.assertEqual(parsed, open(name + '.parsed').read())

    def test_utf8(self):
        self.parse_file('fixtures/coding.utf8.txt')

    def test_cp1250(self):
        self.parse_file('fixtures/coding.cp1250.txt')

    def test_iso8859_2(self):
        self.parse_file('fixtures/coding.iso8859_2.txt')

if __name__ == '__main__':
    unittest.main()
