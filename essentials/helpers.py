import string
import random


def get_url(length: int) -> str:
    return "".join(random.choices(string.hexdigits, k=length))
