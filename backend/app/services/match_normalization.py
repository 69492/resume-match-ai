import re


def match_key(value: str) -> str:
    """Return a conservative identity key for requirement labels.

    Requirement labels can differ harmlessly in case, whitespace, or punctuation
    (for example, ``Full Stack Development`` and ``Full-Stack Development``).
    Tokenizing punctuation keeps those variants equivalent without introducing
    fuzzy matching or accepting an unrelated LLM-generated claim.
    """
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))
