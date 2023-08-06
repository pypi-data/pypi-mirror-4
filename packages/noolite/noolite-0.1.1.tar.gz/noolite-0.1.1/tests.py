import unittest

import noolite

class Tests(unittest.TestCase):
    def test_init_ch_type(self):
        with self.assertRaises(ValueError):
            n = noolite.NooLite(channals="bla")
            n = noolite.NooLite(idVendor="bla")

    def test_init_idVendor_type(self):
        with self.assertRaises(ValueError):
            n = noolite.NooLite(idVendor="bla")

    def test_init_idProduct_type(self):
        with self.assertRaises(ValueError):
            n = noolite.NooLite(idProduct="bla")

    def test_ch_str(self):
        n = noolite.NooLite()
        self.assertEqual(n.on("8"), 0)

    def test_ch_int(self):
        n = noolite.NooLite()
        self.assertEqual(n.off("8"), 0)

    def test_ch_negative(self):
        n = noolite.NooLite()
        self.assertRaises(noolite.NooLiteErr, n.on, -1)

    def test_ch_too_big(self):
        n = noolite.NooLite()
        self.assertRaises(noolite.NooLiteErr, n.on, 42)

if __name__ == '__main__':
    print "Pay attantion tests will work with 8 channel. Are you sure [Y]? "
    if raw_input() == 'Y':
        unittest.main()
    else:
        print "Exit"
