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


_EXPERIMENT_TIME = re.compile(
    r"(?<!\d)(?:(?:19|20)\d{2}(?:[-_.]?\d{2}){0,2})(?!\d)"
    r"|(?<!\d)(?:[01]\d|2[0-3])[:_.-][0-5]\d(?:[:_.-][0-5]\d)?(?!\d)"
    r"|(?<!\d)(?:[01]\d|2[0-3])[0-5]\d[0-5]\d(?:z|utc)(?![a-z])",
    re.IGNORECASE,
)
_EXPERIMENT_OPAQUE = re.compile(
    r"(?<![a-z0-9])(?:[0-9a-f]{7,}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})(?![a-z0-9])",
    re.IGNORECASE,
)


def experiment_name_violation(path, is_directory):
    """Validate a directory name or filename stem inside the experiment tree."""
    name = path.name if is_directory else path.stem
    if (is_directory and name == "tmp") or (not is_directory and (path.name == "README.md" or is_configuration_file(path))):
        return None
    if _EXPERIMENT_TIME.search(path.name):
        return "experiment_name", "Keep calendar dates and times in the run record"
    if _EXPERIMENT_OPAQUE.search(path.name):
        return "experiment_name", "Keep opaque execution identifiers in the run record"
    if not contains_english_word(name):
        return "name_english_word", "Use at least one complete English word in each experiment path segment"
    return None
