'''
password module generates random passcodes
'''

import random
from pkg.tools import converter


def get_password(length: int, skip_symbol: bool = False):
    alphabets = __get_alphabets()
    numbers = __get_numbers()
    symbols = __get_symbols()

    if skip_symbol:
        collection = alphabets + numbers
    else:
        collection = alphabets + numbers + symbols
    return __generate_passcode(length=length, collection=collection)

def __generate_passcode(length: int, collection: list) -> str:
    random.shuffle(collection)
    randomness = []
    for _ in range(length):
        randomness.append(random.choice(collection))
    passcode = ''.join(converter.decimals_to_asciis(*randomness))
    return passcode

def __get_alphabets() -> list:
    alphabets = (range(65, 91), range(97, 123))
    result = []
    for alphabet in alphabets:
        for i in alphabet:
            result.append(i)
    return result

def __get_numbers() -> list:
    numbers = range(48, 58)
    result = []
    for number in numbers:
        result.append(number)
    return result

def __get_symbols() -> list:
    symbols = (range(33, 48), range(58, 65), range(91, 97), range(123, 127))
    result = []
    for symbol in symbols:
        for i in symbol:
            result.append(i)
    return result
