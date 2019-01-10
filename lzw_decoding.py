import sys
import math
import os
import time
# Class for bit reading


class BitReader(object):
    def __init__(self, f):
        self.input = f
        self.accumulator = 0
        self.bcount = 0
        self.read = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _readbit(self):
        if not self.bcount:
            a = self.input.read(1)
            if a:
                self.accumulator = ord(a)
            self.bcount = 8
            self.read = len(a)
        rv = (self.accumulator & (1 << self.bcount - 1)) >> self.bcount - 1
        self.bcount -= 1
        return rv

    def readbits(self, n):
        v = 0
        while n > 0:
            v = (v << 1) | self._readbit()
            n -= 1
        return v


def decompress(input, output):
	frozen = False
	module_name = os.path.splitext(os.path.basename(__file__))[0]
	bitio = __import__(module_name)
	with open(input, "rb") as rf:
		with open(output, "wb") as wf:
			with bitio.BitReader(rf) as reader:

				dict_size = 256
				dictionary = {i: format(i, "08b") for i in range(dict_size)}

				dict_limit = 2**ord(rf.read(1))
				dict_freeze = reader._readbit()

				print("Spaudimo parametrai: ")
				if dict_limit == 1:
					print("Maksimalus žodyno dydis neribojamas")
				else:
					print("Maksimalus žodyno dydis: ", dict_limit)
					if dict_freeze:
						print("Pasiekus ribą, žodynas šaldomas")
					else:
						print("Pasiekus ribą, žodynas trinamas")

				# on j depends size of dynamically written bits
				j = 1
				number = numberofbits(j)
				k1 = reader.readbits(number)
				w = format(k1, "08b")
				n = int(w, 2)
				wf.write(bytes([int(dictionary[n], 2)]))

				while True:
					# dict reset and freeze same as encoding
					if dict_size == dict_limit and dict_freeze:
						frozen = True
					elif dict_size == dict_limit and not dict_freeze:
						dict_size = 256
						dictionary = {i: format(i, "08b") for i in range(dict_size)}
					if dict_size == dict_limit - 1 and not dict_freeze:  # hack, but works
						j = 0
					if not frozen:
						j = j + 1
					number = numberofbits(j)
					k1 = reader.readbits(number)  # read as many bits as encoded dynamically
					if not reader.read:  # if end of file
						break
					number2 = "0" + str(number) + "b"
					k1 = format(k1, number2)
					k = int(k1, 2)

					if k in dictionary:
						entry = dictionary[k]
					elif k == dict_size:
						entry = w + w[0:8]
					else:
						raise ValueError('bad!')

					for i in range(0, len(entry), 8):
						temp = entry[i:i+8]
						wf.write(bytes([int(temp, 2)]))

					if not frozen:
						dictionary[dict_size] = w + entry[0:8]
						w = entry
						dict_size += 1
					else:
						w = ""


def numberofbits(k):
	return int(math.log2(256+k)+1)


def main():
	if len(sys.argv) < 3:
		print("Trūksta argumentų.")
		print("Programos naudojimo pavyzdys:")
		print(sys.argv[0] + " [koduojamas failas] [užkoduotas failas]")
		sys.exit()
	elif len(sys.argv) > 3:
		print("Per daug argumentų.")
		print("Programos naudojimo pavyzdys:")
		print(sys.argv[0] + " [koduojamas failas] [užkoduotas failas]")
		sys.exit()
		
	input = sys.argv[1]
	output = sys.argv[2]
	start_time = time.time()
	decompress(input, output)
	print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__": main()