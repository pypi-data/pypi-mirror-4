import sys
import codecs
import locale

def encode_output():
    enc = locale.getpreferredencoding()
    writer = codecs.getwriter(enc)
    if not sys.stdout.isatty():
        sys.stdout = writer(sys.stdout)
    if not sys.stderr.isatty():
        sys.stderr = writer(sys.stderr)
