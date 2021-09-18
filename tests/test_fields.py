import unittest
import field_info


class TestField(unittest.TestCase):
    def test_xref(self):
        info = field_info.Field()
        line = 'X:23'
        info(line)
        self.assertEqual(23, info.xref)

    def test_meter(self):
        info = field_info.Field()
        info.do_tune = True
        line = 'M: 6/8'
        info(line)
        self.assertEqual((6, 8), info.meter)

    def test_length(self):
        info = field_info.Field()
        info.do_tune = True
        line = 'L: 1/4'
        info(line)
        self.assertEqual((1, 4), info.length)

    def test_title(self):
        info = field_info.Field()
        info.do_tune = True
        line = 'T: First'
        info(line)
        self.assertTrue('First', info.titles[0])
        line = 'T: second'
        info(line)
        self.assertEqual('second', info.titles[1])
        line = 'T: third'
        info(line)
        self.assertEqual('third', info.titles[2])
        line = 'T: many'
        info(line)
        self.assertTrue('many' not in info.titles)
        self.assertEqual(3, len(info.titles))

    def test_rhythm(self):
        info = field_info.Field()
        info.do_tune = True
        line = 'R: hornpipe'
        info(line)
        self.assertEqual('hornpipe', info.rhythm)

    def test_clef(self):
        info = field_info.Field()
        info.do_tune = True
        line = 'K: A'
        info(line)
        self.assertEqual('G', info.clef)

    def test_key(self):
        info = field_info.Field()
        info.do_tune = True
        line = 'K:Dmaj'
        info(line)
        self.assertEqual('Dmaj', info.key)


if __name__ == '__main__':
    unittest.main()
