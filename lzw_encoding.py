import sys
import math
import time
# Class for bit operations - write


class BitWriter(object):
    def __init__(self, f):
        self.accumulator = 0
        self.bcount = 0
        self.out = f

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()

    def __del__(self):
        try:
            self.flush()
        except ValueError:  # I/O operation on closed file.
            pass

    def _writebit(self, bit):
        if self.bcount == 8:
            self.flush()
        if bit > 0:
            self.accumulator |= 1 << 7 - self.bcount
        self.bcount += 1

    def writebits(self, bits, n):
        while n > 0:
            self._writebit(bits & 1 << n - 1)
            n -= 1

    def flush(self):
        self.out.write(bytearray([self.accumulator]))
        self.accumulator = 0
        self.bcount = 0


def compress(input, output, dict_limit, dict_freeze):
    frozen = False
    import os
    module_name = os.path.splitext(os.path.basename(__file__))[0]
    bitio = __import__(module_name)
    with open(input, "rb") as rf:
        with open(output, "wb") as wf:
            with bitio.BitWriter(wf) as writer:
                # init dictionary
                dict_size = 256
                dictionary = {format(i, "08b"): i for i in range(dict_size)}
                # writing decoding params
                if 2 ** dict_limit < 257:
                    dict_limit = 0
                    print("Žodyno dydis neribojamas!")
                writer.writebits(dict_limit, 8)
                writer._writebit(dict_freeze)
                dict_limit = 2 ** dict_limit
                w = ""
                k = 0
                while True:
                    if dict_size == dict_limit and dict_freeze:
                        frozen = True
                    # if dictionary limit is reached and dictionary not frozen - resetting dictionary
                    # and k for dynamic bit writing
                    elif dict_size == dict_limit and not dict_freeze:
                        dict_size = 256
                        dictionary = {format(i, "08b"): i for i in range(dict_size)}
                        k = 0
                    c = rf.read(1)  # reading one byte
                    if not c:  # if end of file - break
                        break
                    c = bin(ord(c))[2:].rjust(8, '0')  # our letter in dictionary is string of bits: "00001010", not A,B
                    wc = w + c  # w+c is also just bit sequence
                    if wc in dictionary:
                        w = wc
                    else:
                        if not frozen:
                            k = k+1
                        # writing dictionary reference (number - 62, 13 etc) to answer
                        # size of bits depends on k: to write number 1026 we need 11 bits "10000000010"
                        number = numberofbits(k)
                        number2 = "0"+str(number)+"b"
                        n = format(dictionary[w], number2)
                        writer.writebits(int(n, 2), number)
                        if not frozen:
                            dictionary[wc] = dict_size
                            dict_size += 1
                        w = c
                # writing whats left
                if w:
                    number = numberofbits(k)
                    number2 = "0" + str(number) + "b"
                    n = format(dictionary[w], number2)
                    writer.writebits(int(n, 2), number)


def numberofbits(k):
    return int(math.log2(256+k)+1)

def main():
    if len(sys.argv) < 5:
        print("Trūksta argumentų.")
        print("Programos naudojimo pavyzdys:")
        print(sys.argv[
                  0] + " [koduojamas failas] [užkoduotas failas] [skaičius n: 2^n = žodyno riba] [šaldyti ar ištrinti žodyną (0 arba 1)]")
        sys.exit()
    elif len(sys.argv) > 5:
        print("Per daug argumentų.")
        print("Programos naudojimo pavyzdys:")
        print(sys.argv[
                  0] + " [koduojamas failas] [užkoduotas failas] [skaičius n: 2^n = žodyno riba] [šaldyti ar ištrinti žodyną (0 arba 1)]")
        sys.exit()

    input = sys.argv[1]
    output = sys.argv[2]
    dict_limit = int(sys.argv[3])
    dict_freeze = int(sys.argv[4])
    start_time = time.time()
    compress(input, output, dict_limit, dict_freeze)
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__": main()
