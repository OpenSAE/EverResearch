"""Check if the root name of the project and the project’s own file name contains readable English words.

Catalogues and documents for layout and experimental inspection to validate project maintenance, external originals processed according to their respective layout rules.
"""

from functools import lru_cache
import re


ENGINEERING_WORDS = frozenset({
    "dataset", "datasets", "filename", "filenames", "metadata", "postprocessing",
    "precheck", "preprocessing", "runtime", "runtimes", "tokenization", "tokenizer",
    "tokenizers", "wildcard", "wildcards", "workflow", "workflows",
})
INITIALISMS = frozenset({"ai", "id", "io", "os"})
FIXED_FILES = frozenset({"README.md", "__init__.py", "py.typed", "conftest.py"})
PROJECT_WORD = r"[A-Z][a-z]+"


@lru_cache(maxsize=1)
def english_dictionary():
    from spellchecker import SpellChecker

    return SpellChecker(language="en").word_frequency.dictionary


def contains_english_word(name):
    """Match a whole token, optionally followed by a component's version digits."""
    words = re.split(r"[_+.-]|(?<=[a-z])(?=[A-Z])", name)
    for part in words:
        word = part.rstrip("0123456789").lower()
        if (re.fullmatch(r"[a-z]{2,}", word) and word not in INITIALISMS
                and (word in ENGINEERING_WORDS or word in english_dictionary())):
            return True
    return False


def project_name_valid(name):
    return bool(re.fullmatch(rf"(?:{PROJECT_WORD}){{2,3}}", name) and contains_english_word(name))


def path_name_violations(entry, is_directory, *, allow_digits=False):
    if not is_directory and entry.name in FIXED_FILES:
        return
    name = entry.name if is_directory else entry.stem
    if not is_directory and name.startswith("test_"):
        name = name.removeprefix("test_")
    if not allow_digits and re.search(r"[0-9]", name):
        yield "name_digits", "Duty words for custom catalogues and file names; version numbers for real models or data set identities"
    if not contains_english_word(name):
        yield "name_english_word", "The name contains at least one full English word and separates words by underlineding"


def is_configuration_file(path):
    return path.stem == "config" and path.suffix in {".json", ".yaml", ".yml", ".toml"}
