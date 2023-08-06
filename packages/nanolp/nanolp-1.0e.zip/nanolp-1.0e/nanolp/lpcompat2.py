StringTypes23 = (str, unicode)

# XXX Usage of codecs.open() causes errors in re-expr, so fread23() is implemented
def fread23(filename):
    with open(filename, 'rt') as f:
        return f.read().decode('utf8')

def fwrite23(filename, text):
    with open(filename, 'wt') as f:
        f.write(text.encode('utf8', errors='replace'))

def bytestostr23(b):
    return str(b)

def strtobytes23(s):
    return bytes(s)

def reraise23(exc, msg, tb):
    raise exc, msg, tb

