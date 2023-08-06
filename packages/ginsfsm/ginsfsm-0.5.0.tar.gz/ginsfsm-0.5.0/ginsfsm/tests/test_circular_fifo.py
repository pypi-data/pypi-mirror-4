import unittest
from ginsfsm.circular_fifo import (
    CircularFIFO,
    CircularFullBufferError,
)


class TestCircular(unittest.TestCase):
    def setUp(self):
        self.circular = CircularFIFO(5)

    def test_getdata_putdata_without_overwrite(self):
        data = self.circular.getdata(1)
        self.assertEqual(data, b'')

        count = self.circular.free_space
        self.assertEqual(count, 5)

        count = self.circular.putdata(b"123")
        self.assertEqual(count, 3)
        count = self.circular.free_space
        self.assertEqual(count, 2)

        count = self.circular.putdata(b"ab")
        self.assertEqual(count, 2)
        count = self.circular.free_space
        self.assertEqual(count, 0)

        self.assertRaises(CircularFullBufferError,
            self.circular.putdata,
            b"XX")

        data = self.circular.getdata(5)
        self.assertEqual(data, b"123ab")

        data = self.circular.getdata(1)
        self.assertEqual(data, b'')

        count = self.circular.putdata(b"qw")
        self.assertEqual(count, 2)
        data = self.circular.getdata()
        self.assertEqual(data, b'qw')

    def test_getdata_putdata_with_overwrite(self):
        count = self.circular.putdata(b"123")
        self.assertEqual(count, 3)
        count = self.circular.free_space
        self.assertEqual(count, 2)

        self.assertRaises(CircularFullBufferError,
            self.circular.putdata,
            b"abc")

        data = self.circular.getdata(2)
        self.assertEqual(data, b"12")
        count = self.circular.free_space
        self.assertEqual(count, 4)
        count = self.circular.busy_space
        self.assertEqual(count, 1)

        count = self.circular.putdata(b"abcd")
        self.assertEqual(count, 4)

        data = self.circular.getdata(0)
        self.assertEqual(data, b"3abcd")
        count = self.circular.free_space
        self.assertEqual(count, 5)

        count = self.circular.putdata(b"zxcvb")
        self.assertEqual(count, 5)
        count = self.circular.free_space
        self.assertEqual(count, 0)

        data = self.circular.getdata(4)
        self.assertEqual(data, b"zxcv")
        count = self.circular.free_space
        self.assertEqual(count, 4)

        data = self.circular.getdata(3)
        self.assertEqual(data, b"b")
        count = self.circular.free_space
        self.assertEqual(count, 5)

    def test_getdata_putdata_with_ln(self):
        s = bytearray(b'123')
        count = self.circular.putdata(s, 2)
        self.assertEqual(count, 2)
        count = self.circular.free_space
        self.assertEqual(count, 3)

        s = b"abc"
        count = self.circular.putdata(s, 5)
        self.assertEqual(count, 3)
        count = self.circular.free_space
        self.assertEqual(count, 0)

        data = self.circular.getdata()
        self.assertEqual(data, b"12abc")

if __name__ == "__main__":
    circular = CircularFIFO(5)

    circular.putdata(b"123")
    print(circular)
    circular.getdata(2)
    print(circular)

    circular.putdata(b"abcd")
    print(circular)

    circular.getdata(0)
    print(circular)
