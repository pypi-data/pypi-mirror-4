def skip_bigrams(tokens, skip):
    bigrams = []
    for i in range(len(tokens)-1):
        for skip_count in range(skip+1):
            if i+skip_count+2 <= len(tokens):
                bigrams.append(u'_'.join([tokens[i], tokens[i+skip_count+1]]))
    return bigrams
