import re

def contains(string, substring=None):
    """
    Check if $typed in $text

    check_matching('du', 'adfDU'): True
    check_matching('fda', 'fdbadafa'): False
    """
    res = re.search(substring, string, re.I)
    return True if res else False

