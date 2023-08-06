import sys
import keyword
import collections

counter = collections.Counter()
keywords = set(keyword.kwlist)

for line in sys.stdin:
    words = [word.lower() for word in line.strip().split()]
    for word in words:
        if word not in keywords:
            continue
        counter[word.lower()] += 1

for key in counter:
    print(", ".join([str(counter[key]), key]))
