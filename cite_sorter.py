# coding=utf-8
"""
@author: John Mark Mayhall
Last Edit: 06/11/2026
Function for ensuring in-text citations are order chronological and then alphabetically.
"""
import re
from pathlib import Path

TEX_FILE = "C:/Users/jmayhall/Downloads/masters_paper/amspaperV6.1.tex"
BIB_FILE = "C:/Users/jmayhall/Downloads/masters_paper/references.bib"


def load_bib_years(bib_file: str) -> dict[str, int]:
    """
    Function for reading bib file and getting the years.
    :param bib_file: Bib file path.
    :return: dictionary of citation_key -> year.
    """
    text = Path(bib_file).read_text(encoding="utf-8")

    years = {}

    # Find each BibTeX entry
    entry_pattern = re.compile(
        r'@\w+\s*\{\s*([^,]+),(.*?)\n\}',
        re.DOTALL | re.IGNORECASE
    )

    for entry in entry_pattern.finditer(text):
        key = entry.group(1).strip()
        body = entry.group(2)

        year_match = re.search(
            r'year\s*=\s*\{?(\d{4})\}?',
            body,
            re.IGNORECASE
        )

        if year_match:
            years[key] = int(year_match.group(1))
        else:
            years[key] = 9999
            print(f"Warning: no year found for {key}")

    return years


def citation_sort_key(key: str, years: dict) -> tuple[int, str]:
    """
    Function for getting the year for each key.
    :param key: Current citation key.
    :param years: Year dictionary.
    :return: Tuple of year and citation key .
    """
    return (
        years.get(key, 9999),
        key.lower()
    )


def reorder_citation(match: re.Match, years: dict[str, int]) -> str:
    """
    Function for reordering citations.
    :param match: Regex match object.
    :param years: Year dictionary.
    :return: Command string.
    """
    command = match.group(1)
    citation_text = match.group(2)

    citations = [c.strip() for c in citation_text.split(",")]
    sorted_citations = sorted(
        citations,
        key=lambda c: citation_sort_key(c, years)
    )

    if citations != sorted_citations:
        print("\nChanged:")
        print(f"  Before: {command}{{{', '.join(citations)}}}")
        print(f"  After : {command}{{{', '.join(sorted_citations)}}}")

    return f"{command}{{{', '.join(sorted_citations)}}}"


def main() -> None:
    """
    Main function for running the reorder citation code.
    :return: Nothing.
    """
    years = load_bib_years(BIB_FILE)

    tex_path = Path(TEX_FILE)
    original = tex_path.read_text(encoding="utf-8")

    cite_pattern = re.compile(
        r'(\\cite[a-zA-Z*]*)\{([^}]*)\}'
    )

    modified = cite_pattern.sub(
        lambda m: reorder_citation(m, years),
        original
    )

    if modified == original:
        print("No changes needed.")
        return

    backup = tex_path.with_suffix(tex_path.suffix + ".bak")
    backup.write_text(original, encoding="utf-8")

    tex_path.write_text(modified, encoding="utf-8")

    print("\nFinished.")
    print(f"Backup written to: {backup}")


if __name__ == "__main__":
    main()