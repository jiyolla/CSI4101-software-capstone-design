import sys, os

with open(os.path.join(sys.path[0], '..', 'README.md'), 'r') as f:
    print(f.read())
