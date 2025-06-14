from difflib import SequenceMatcher
from hashlib import sha256, md5

_TOKEN_CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#%()*+,-./:;=?@[]^_`{|}~"

def remove_duplicates(items: list) -> list:
    seen = []
    result = []
    for item in items:
        if item not in seen:
            seen.append(item)
            result.append(item)
    return result

def lists_equal_ignore_order(a: list, b: list) -> bool:
    if len(a) != len(b):
        return False

    b_copy = b[:]
    for item in a:
        try:
            b_copy.remove(item)  # uses __eq__, safe for mutable objects
        except ValueError:
            return False
    return not b_copy

def get_closest_matches(string, possible_values: list[str], n: int) -> list[str]:
    similarity_scores = [(item, SequenceMatcher(None, string, item).ratio()) for item in possible_values]
    sorted_matches = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    return [i[0] for i in sorted_matches[:n]]   

def tuplify(obj):
    if isinstance(obj, list):
        return tuple(tuplify(item) for item in obj)
    elif isinstance(obj, dict):
        return {tuplify(key): tuplify(value) for key, value in obj.items()}
    elif isinstance(obj, (set, tuple)):
        return type(obj)(tuplify(item) for item in obj)
    else:
        return obj

def string_to_sha256(primary: str, secondary: str|None=None) -> str:
    def _string_to_sha256(input_string: str, digits: int) -> str:
        hex_hash = sha256(input_string.encode()).hexdigest()

        result = []
        for i in range(digits):
            chunk = hex_hash[i * 2:(i * 2) + 2]
            index = int(chunk, 16) % len(_TOKEN_CHARSET)
            result.append(_TOKEN_CHARSET[index])
        return ''.join(result)

    if secondary is None:
        return _string_to_sha256(primary, digits=20)
    else:
        return _string_to_sha256(primary, digits=16) + _string_to_sha256(secondary, digits=4)

def number_to_token(number: int) -> str:
    base = len(_TOKEN_CHARSET)
    result = []
    while number > 0:
        number -= 1
        result.insert(0, _TOKEN_CHARSET[number % base])
        number //= base
    return ''.join(result)

def generate_md5(data: bytes) -> str:
    """
    Generate an MD5 hash for a given bytes object.

    Args:
        data: the input data in bytes

    Returns:
        A hexadecimal MD5 hash string
    """
    md5_hash = md5()
    for i in range(0, len(data), 4096):
        md5_hash.update(data[i:i+4096])
    return md5_hash.hexdigest()


__all__ = [
    "remove_duplicates", "lists_equal_ignore_order", "get_closest_matches", "tuplify", 
    "string_to_sha256", "number_to_token", "generate_md5",
]

