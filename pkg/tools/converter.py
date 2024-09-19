'''
ascii module converts ASCII characters to string and vice versa
'''

def decimal_to_ascii(decimal_input: int) -> str:
    return chr(decimal_input)

def ascii_to_decimal(ascii_input: str) -> int:
    return ord(ascii_input)

def decimals_to_asciis(*args: int) -> tuple:
    try:
        return tuple([decimal_to_ascii(i) for i in args])
    except Exception as exc:
        raise TypeError(f"Unexpected type argument: {type(*args)}.\nExpected: *[1, 2, 3] or *(1, 2, 3)") from exc

def asciis_to_decimals(*args: str) -> tuple:
    try:
        return tuple([ascii_to_decimal(i) for i in args])
    except Exception as exc:
        raise TypeError(f"Unexpected type argument: {type(*args)}\nExpected: *['A', 'B', 'C'] or *('A', 'B', 'C')") from exc
