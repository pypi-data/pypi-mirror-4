
def rgb_to_cairo_rgb(rgb):
    ratio = 1.0 / 255.0
    return tuple(map(lambda x: x* ratio, rgb))

def tuple_items_to_float(t):
    return tuple(map(lambda x: float(x), t))

def float_to_upper_rounded_int(f):
    i = int(f)
    if f % 2:
        i += 1
    return i
