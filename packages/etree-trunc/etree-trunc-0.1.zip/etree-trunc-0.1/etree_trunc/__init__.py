"""Main function for truncating."""
import re

WHITESPACE = re.compile(r'(\S+)')

def _tokenize(text):
    tokens = re.split(WHITESPACE, text)
    while tokens:
        white = tokens.pop(0)
        word = tokens.pop(0) if tokens else ''
        yield white, word


def _truncate_text(text, maxlen, ellipsis):
    """Truncate a string to a given length."""
    buf = []
    used = 0
    for white, word in _tokenize(text):
        len_ = len(word) + len(white)
        if used + len_ > maxlen:
            buf.append(ellipsis)
            break
        else:
            buf.append(white)
            buf.append(word)
            used += len_
    return ''.join(buf)


def truncate(el, maxlen, ellipsis='...'):
    """Truncate the element in place to given maxlen.
    Returns None if object was truncated or the number of chars left."""
    if maxlen is None:
        el.text = ''
        el.tail = ''
    else:
        if el.text and len(el.text) > maxlen:
            el.text = _truncate_text(el.text, maxlen, ellipsis)
            el.tail = ''
            maxlen = None
        else:
            maxlen -= len(el.text or '')
            if el.tail and len(el.tail) > maxlen:
                el.tail = _truncate_text(el.tail, maxlen, ellipsis)
                maxlen = None
            else:
                maxlen -= len(el.tail or '')
    for child in el:
        maxlen = truncate(child, maxlen, ellipsis)
    return maxlen
