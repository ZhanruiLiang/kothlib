import sys
import random

for line in sys.stdin:
    line = line.rstrip()
    if line == 'quit':
        break
    if line == 'choose':
        print(random.choice(('rock', 'paper', 'scissors')))
        sys.stdout.flush()
