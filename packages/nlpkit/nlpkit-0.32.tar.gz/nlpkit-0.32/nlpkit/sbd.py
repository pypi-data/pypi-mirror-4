from pprint import pprint
import unicodedata

def extract_features(left_tokens, right_tokens):
    right_tok = right_tokens[0]
    left_tok = left_tokens[-1]

    feats = {'left_tok': left_tok,
             'right_tok': right_tok,
             'left_tok_len': len(left_tok),
             'right_tok_capitalized': 'u' in unicodedata.category(right_tok[0]),
             }
            # Two features which depend on global counts are omitted

    feats['left_tok+right_tok'] = feats['left_tok'] + '+' + feats['right_tok']
    feats['left_tok+right_tok_capitalized'] = u'{}+{}'.format(feats['left_tok'], feats['right_tok_capitalized'])

    return feats


if __name__ == '__main__':
    feats = extract_features(u"This is Mr".split(" "), u"Spike Jones".split(" "))
    pprint(feats)



