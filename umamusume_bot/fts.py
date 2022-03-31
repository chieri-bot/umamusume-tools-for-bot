import difflib


def get_str_similarity(str1: str, str2: str, textlower=True) -> float:
    if textlower:
        str1 = str1.lower()
        str2 = str2.lower()
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()
