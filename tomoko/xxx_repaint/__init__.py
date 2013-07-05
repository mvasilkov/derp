from PIL import Image
from itertools import islice

def int_to_pixel(n):
    return (int(n & 0xff0000) >> 16,
            int(n & 0x00ff00) >> 8,
            int(n & 0x0000ff))

def pixel_to_int(raw):
    return raw[0] << 16 | raw[1] << 8 | raw[2]

def break_bits(im, n):
    return Image.eval(im, lambda c: c & 256 - 2 ** n)

def break_pixel(val, n):
    return tuple(c & 256 - 2 ** n for c in val)

class Mipmap:
    def __init__(self, im, n_levels):
        self.levels = [break_bits(im, n) for n in xrange(n_levels)]
        self.n_levels = n_levels

    def __getitem__(self, pos):
        return self.levels[0].getpixel(pos)

    def cons(self, start_u, start_v):
        end = self.n_levels - 1
        start_u -= end
        start_v -= end

        for v in xrange(self.n_levels):
            for u in xrange(self.n_levels):
                if u == end and v == end:
                    return
                uu = u + start_u
                vv = v + start_v
                if uu | vv < 0:
                    yield None
                else:
                    level = max(end - u, end - v)
                    yield self.levels[level].getpixel((uu, vv))

class Canvas(Mipmap):
    def __init__(self, size, n_levels):
        self.levels = [Image.new("RGB", (size, size), (0, 0, 0))
            for n in xrange(n_levels)]
        self.n_levels = n_levels

    def future_cons(self, u, v):
        cons_len = self.n_levels ** 2 - 1
        return (islice(self.cons(u, v + n), cons_len - self.n_levels * n)
            for n in xrange(1, self.n_levels))

    def paint(self, u, v, val):
        for n in xrange(self.n_levels):
            self.levels[n].putpixel((u, v), break_pixel(val, n))

    def save(self, filename):
        self.levels[0].save(filename, "PNG")

class Futures:
    def __init__(self, mm, start_u, start_v):
        cons_len = mm.n_levels ** 2
        size = mm.levels[0].size[0]
        result = []
        for v in xrange(mm.n_levels):
            for u in xrange(mm.n_levels):
                if u == 0 and v == 0:
                    continue
                cons_len -= 1
                if u + start_u >= size:
                    continue
                cons = mm.cons(u + start_u, v + start_v)
                result.append(tuple(islice(cons, cons_len)))
        self.conses = tuple(result)