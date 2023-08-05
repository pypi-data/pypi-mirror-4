import re

SMALL = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90
}

MAGNITUDE = {
    'thousand': 1000,
    'million': int(1E6),
    'billion': int(1E9),
    'trillion': int(1E12),
    'quadrillion': int(1E15),
    'quintillion': int(1E18),
    'sextillion': int(1E21),
    'septillion': int(1E24),
    'octillion': int(1E27),
    'nonillion': int(1E30),
    'decillion': int(1E33),
}

_SINGLE_NUMBER_PTN = r'|'.join(re.escape(numword) 
    for numword in SMALL.keys() + MAGNITUDE.keys() + ['hundred'])
SPELLED_NUMBER_RE = re.compile(r'\b(?:%s)(?:(?:,?\s+|-|\s+and\s+)(?:%s))*\b' % (
    _SINGLE_NUMBER_PTN, _SINGLE_NUMBER_PTN), re.IGNORECASE)


class NumberException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

def spelled_num_to_digits(spelled_num):
    """
    >>> assert 1 == spelled_num_to_digits("one")
    >>> assert 12 == spelled_num_to_digits("twelve")
    >>> assert 72 == spelled_num_to_digits("seventy-two")
    >>> assert 300 == spelled_num_to_digits("Three hundred")
    >>> assert 1200 == spelled_num_to_digits("TWELVE HUNDRED")
    >>> assert 12304 == spelled_num_to_digits("twelve thousand three hundred four")
    >>> assert 12506 == spelled_num_to_digits("twelve thousand, five hundred and six")
    >>> assert 6000000 == spelled_num_to_digits("six Million")
    >>> assert 6400005 == spelled_num_to_digits("six million four hundred thousand five")
    >>> assert 123456789012 == spelled_num_to_digits(
    ...   'one hundred twenty three billion, four hundred fifty six million, seven hundred eighty nine thousand twelve')
    >>> assert 4E33 == spelled_num_to_digits("four decillion")
    """
    words = re.split(r",?\s+|-", spelled_num.lower())
    major = 0
    units = 0
    for w in words:
        x = SMALL.get(w, None)
        if x is not None:
            units += x
        elif w == "hundred":
            units *= 100
        elif w == "and":
            continue
        else:
            x = MAGNITUDE.get(w, None)
            if x is not None:
                major += units * x
                units = 0
            else:
                raise NumberException("Unknown number: %s" % w)
    return major + units
    
    
def replace_spelled_numbers(sentence):
    """
    >>> assert replace_spelled_numbers('There are TEN sponges') == 'There are 10 sponges'
    >>> assert replace_spelled_numbers('I got ninety nine problems') == 'I got 99 problems'
    >>> assert replace_spelled_numbers('He got two million, one hundred and eighty-two thousand, three hundred and two problems') == 'He got 2182302 problems'
    >>> assert replace_spelled_numbers('I have five coconuts and two hundred and thirty-three carrots') == 'I have 5 coconuts and 233 carrots'
    """
    def try_spelled_num_to_digits(text):
        try:
            return spelled_num_to_digits(text)
        except NumberError:
            return text
    return SPELLED_NUMBER_RE.sub(
        lambda m: str(try_spelled_num_to_digits(m.group())), sentence)


    
if __name__ == "__main__":
    import doctest
    doctest.testmod()