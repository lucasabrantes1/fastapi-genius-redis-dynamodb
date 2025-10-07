import re


def norm_artist(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())