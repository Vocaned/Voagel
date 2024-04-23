from typing import List
from pycountry import languages

async def language_autocomplete(_, string: str) -> List[str]:
    """Autocomplete languages with alpha2 codes"""
    out = []

    for lang in languages.objects:
        try:
            if string.lower() in lang.name.lower() and lang.alpha_2:
                out.append(lang.name)
        except Exception:
            pass

    return out[:25]

