# -*- coding: utf-8 -*-
""" FIFO queue implemented with a CircularFIFO buffer.
    It's not thread-safe.
"""
DEFAULT_CIRCULAR_SIZE = 8192


class CircularFullBufferError(Exception):
    """ Raised when CircularFIFO have problems."""


class CircularFIFO(object):
    def __init__(self, size=DEFAULT_CIRCULAR_SIZE):
        """ CircularFIFO buffer.
        """
        self.size = size
        self.start = 0
        self.count = 0
        self.data = bytearray(size)

    def __str__(self):
        return "size %d, count %d, start %d, data %s" % (
            self.size,
            self.count,
            self.start,
            self.data,
        )

    def putdata(self, bf, ln=0):
        """ WRITING: add `ln` bytes of `bf` to cicular fifo.
            If `ln` is 0 then put all data.
            If `ln` is greater than data len, then `ln` is limited to data len.
            Return number of written bytes.
        """
        if ln <= 0:
            ln = len(bf)
        if ln > len(bf):
            ln = len(bf)

        if ln == 0:
            return 0

        data = bf[0:ln]

        writted = ln = len(data)
        if ln > self.free_space:
            raise CircularFullBufferError(
                "ERROR full buffer, not space for %d bytes" % (ln,))

        tail = (self.start + self.count) % self.size  # write pointer
        right_len = self.size - tail  # right zone
        self.count += ln
        if ln <= right_len:
            # enough with the right zone
            self.data[tail:tail + ln] = data[:]
        else:
            # put maximum at the right zone
            self.data[tail:tail + right_len] = data[:right_len]
            ln -= right_len

            # put the rest at the left zone
            self.data[0:ln] = data[right_len:]

        return writted

    def getdata(self, ln=0):
        """ READING : Pull 'ln' bytes.
            Return the pulled data.
            If ln is <= 0 then all data is pulled.
            If there is no enough 'ln' bytes, it return all the remaining.
        """
        if ln <= 0 or ln > self.count:
            ln = self.count
        right_len = self.size - self.start  # right zone (from start to end)
        if ln <= right_len:
            # enough with the right zone
            data = self.data[self.start: self.start + ln]
            self.count -= ln
            self.start += ln
        else:
            # get all the right zone
            data = self.data[self.start: self.start + self.size]
            self.count -= ln  # decrement now!
            ln -= self.size - self.start

            # add the rest of the left zone
            data += self.data[0:ln]
            self.start = ln

        return data

    @property
    def busy_space(self):
        """READING: Return number of bytes pending of reading
        """
        return self.count

    @property
    def free_space(self):
        """ WRITTING: Return number of free byte space to write.
        """
        free_bytes = self.size - self.count
        return free_bytes
