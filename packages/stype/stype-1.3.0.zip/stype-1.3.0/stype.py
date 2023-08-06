''' This module is used to find out how many vowels or consonants or symbols/punctuations and also spaces are there in your string and it will also collect the vowels,consonants and symbols/punctuation.
    Function 'count_vowels()' is used to find out how many vowels are there in the string.
    Function 'count_consonants()' is used to find out how many consonants are there in the string.
    Function 'collect_vowels()' is used to collect the vowels.
    Function 'collect_consonants()' is used to collect the consonants.
    Function 'count_symbols()' is used to count the number of symbols/punctuation.
    Function 'collect_symbols()' is used to collect the symbols/punctuation.
    Function 'count_space()' tells you the number of spaces you have used.
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

def count_symbols(s):
    '''

    Return the number of symbols and puncuations in the s.

    >>> count_symbols('Happy Anniversary!')
    1
    >>> count_symbols('cysd')
    0
    >>> count_symbols('Hey!How are you?I am good.')
    3
    '''

    symbols = 0

    for symb in s:
        if symb in '''`~!@#$%^&*()-_=+[]{};:"'\|/?.>,<''':
            symbols = symbols + 1

    return symbols

def collect_symbols(s):
    '''
    Return the symbols and punctions in the s.

    >>> collect_symbols('Happy Anniversary!')
    '!'
    >>> collect_symbols('cysd') 
    ''    
    >>> collect_symbols('Hey!How are you?I am good.')
    '!?.'
    '''

    symbols = ''

    for symb in s:
        if symb in '''`~!@#$%^&*()-_=+[]{};:"'\|/?.>,<''':
            symbols = symbols + symb

    return symbols

def count_space(s):
    '''
    Return the number of spaces you use in s.

    >>> count_space('Hi there , how  are you ')
    7
    >>> count_space('Hi there , how are you ')
    6
    >>> count_space('Hithere,howareyou')
    0
    '''
    space = 0

    for sp in s:
        if sp in ' ':
            space = space + 1

    return space
       
    




















    
            

    
