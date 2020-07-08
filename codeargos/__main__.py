# __main__.py
import sys
from .app import CodeArgos

if __name__ == '__main__':
    CodeArgos.run(sys.argv[1:])