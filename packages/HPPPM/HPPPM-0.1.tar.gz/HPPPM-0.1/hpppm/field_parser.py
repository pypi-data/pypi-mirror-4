#!/usr/bin/env python

import re, sys

__version__ = '0.1'

def tokenizer(input, weedout, split_on='"\s+?"', ignore=[]):
    """ Convert raw input string into units of interest.Weedout and ignore
        text not needed.
    """
    tokens = re.split(split_on, input)

    while tokens:
        token = tokens.pop(0)
        for to_ignore in ignore:
            if re.search(to_ignore, token) is None: 
                yield weedout(token)
        if not ignore:
            yield weedout(token)

def weeder(weed='</|>|<|\"|\''):
    """ Sanitize input - remove weeds/unwanted text
    """

    def weedout(token=None):
        return  re.sub(weed, '', token)

    return weedout

def extractor(tokens, all=[], what=None, how=None, ignore=[]):
    """ Extract tokens embedded between specific tags.One can extract 
        tokens between a specific tag or ask for all tokens embedded
        between all tags of interest.
    """
    start_index, end_index, request = None, None, {}

    if how: return how(tokens, what)

    if what is None:
        for what in all:
            if what not in ignore:
                try:
                    start_index = tokens.index(what)
                    tokens.remove(what)
                    end_index   = tokens.index(what)
                    tokens.remove(what)

                    request[what] = tokens[start_index:end_index]
                except ValueError, err:
                    print "Search for ",what," failed!Error - ", str(err)

        return request
    else:
        try:
            start_index = tokens.index(what)
            tokens.remove(what)
            end_index   = tokens.index(what)
            tokens.remove(what)
        except ValueError, err:
            print str(err)

        return tokens[start_index:end_index]

def parser(inp, extract, sep='"\s+?"', wo='</|>|<|\"|\'', it=[], ig=[]):
    """ Intended interface to the outside unsuspecting world.Takes in the 
        raw input, interested tags, token separator(regexp), unwanted text
        in tokens(regexp), unwanted tokens and all unwanted tokens between 
        specific tags.
    """
    tokens, request = [], {}

    if len(inp) == 1: inputs = inp[1]
    else:             inputs = inp

    weed = weeder(wo)
    if isinstance(inputs, str):
        for token in tokenizer(inputs, weed, sep, ignore=it): tokens.append(token)
    else:
        for token in inputs: tokens.append(weed(token))

    return extractor(tokens, extract, ignore=ig)


if __name__ == '__main__':
    pass
