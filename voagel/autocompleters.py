from typing import List
from pycountry import languages

async def language_autocomplete(_, string: str) -> List[str]:
    """Autocomplete languages with alpha2 codes"""
    langs = []

    for lang in languages:
        try:
            if string.lower() in lang.name.lower() and lang.alpha_2:
                langs.append(lang.name)
        except Exception:
            pass

    return langs[:25]

