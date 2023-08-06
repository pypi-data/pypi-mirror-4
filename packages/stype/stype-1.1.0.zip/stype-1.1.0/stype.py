''' This module is used to find out how many vowels or consonants are there in your string and it will also collect the vowels and consonants.
    Function 'count_vowels' is used to find out how many vowels are there in the string.
    Function 'count_consonants' is used to find out how many consonants are there in the string.
    Function 'collect_vowels' is used to collect the vowels.
    Function 'collect_consonants' is used to collect the consonants.
'''

def count_vowels(s):
    ''' (str) -> int

    Return the number of vowels in s. Do not treat the letter y as a vowel.

    >>> count_vowels('Happy Anniversary!')
    5
    >>> count_vowels('xyz')
    0
    '''

    num_vowels = 0

    for char in s:
        if char in 'aeiouAEIOU':
            num_vowels = num_vowels + 1

    return num_vowels

def count_consonants(s):
    ''' (str) -> int

    Return the number of consonants in s.

    >>> count_consonants('Happy Anniversary!')
    11
    >>> count_consonants('xyz')
    3
    '''

    num_consonants = 0

    for char in s:
        if char in 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ':
            num_consonants = num_consonants + 1

    return num_consonants

def collect_vowels(s):
    ''' (str) -> str

    Return the vowels in s. Do not treat the letter y as a vowel.

    >>> collect_vowels('Happy Anniversary!')
    'aAiea'
    >>> collect_vowels('xyz')
    ''
    '''

    vowels = ''

    for char in s:
        if char in 'aeiouAEIOU':
            vowels = vowels + char
    return vowels

def collect_consonants(s):
    ''' (str) -> str

    Return the consonants in s.

    >>> collect_consonants('Happey Anninversary!')
    'Hppynnnvrsry'
    >>> collect_consonants('eio')
    ''
    '''

    consonants = ''

    for char in s:
        if char in 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ':
            consonants = consonants + char

    return consonants























    
            

    
