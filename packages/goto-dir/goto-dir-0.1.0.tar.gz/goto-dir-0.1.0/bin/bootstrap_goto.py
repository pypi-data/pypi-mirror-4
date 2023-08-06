#!/usr/bin/env python
import sys
from goto import label_main, goto_main


def bootstrap():
    # Remove bootstrap-like string from argv
    del sys.argv[0]

    if 'label' in sys.argv[0]:
        return label_main()
    elif 'goto' in sys.argv[0]:
        return goto_main()
    sys.exit(-1)


if __name__ == '__main__':
    bootstrap()
