import os

VVERSION='0.9.5'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
