StringTypes23 = str

def fread23(filename):
    with open(filename, 'rt', encoding='utf8') as f:
        return f.read()

def fwrite23(filename, text):
    with open(filename, 'wt', encoding='utf8', errors='replace') as f:
        f.write(text)

def bytestostr23(b):
    return str(b, encoding='utf8')

def strtobytes23(s):
    return bytes(s, encoding='utf8')

def reraise23(exc, msg, tb):
    raise exc(msg).with_traceback(tb)
