# __main__.py

import sys
import signal
from .app import CodeArgos

def exit_gracefully(signal, frame):
    sys.exit(0)
    
if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_gracefully)
    CodeArgos.run(sys.argv[1:])

