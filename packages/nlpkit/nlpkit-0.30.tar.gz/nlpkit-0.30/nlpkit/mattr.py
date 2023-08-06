"""Implementation of the Moving Average Type-Token ratio, proposed by Michael A. Covington"""
import numpy as np
from collections import Counter

def mattr(tokens, n=100):
    n = min(len(tokens), n)
    token_counts = Counter(tokens[:n])
    type_count = len(token_counts.keys())
    ratios = [float(type_count) / n]
    for i in range(1, len(tokens)-n+1):
        lost_token = tokens[i-1]
        token_counts[lost_token] -= 1
        if token_counts[lost_token] == 0:
            type_count -= 1

        gained_token = tokens[i+n-1]
        token_counts[gained_token] += 1
        if token_counts[gained_token] > 1:
            type_count += 1
        ratios.append(float(type_count) / n)

#        print "[{}:{}] Lost {}, gained {}".format(i, i+n+1, lost_token, gained_token)
#        print token_counts
    return np.array(ratios).mean()


if __name__ == '__main__':
    seq = "aabbccdefgh"
    print mattr(seq,n=3)
