import json

def f2step(f, step, digits):
    s = f - (f % step)
    s = s + step if f % step != 0 else s
    return round(s, digits)

# range with float support
def rangef(start, stop, step, digits):
    r = start
    while r < stop:
        yield round(r, digits)
        r += step
