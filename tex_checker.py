# coding=utf-8
import re
import language_tool_python


# ============================================================
# HELPERS
# ============================================================

def get_vertical_position(char, page_height):
    if char is None:
        return "unknown position"

    ratio = char["top"] / page_height

    if ratio < 0.33:
        return "upper third"
    elif ratio < 0.66:
        return "middle third"
    return "lower third"


def get_context(text, index, window=50):
    start = max(0, index - window)
    end = min(len(text), index + window)
    snippet = text[start:end].replace("\n", " ")
    return snippet


# ============================================================
# CHECKS
# ============================================================

def check_document(full_text, position_map):

    issues = []

    # --------------------------
    # Patterns
    # --------------------------

    sentence_cap_pattern = re.compile(
        r"([.!?][\]\)\"]?\s+)([a-z])"
    )

    missing_space_pattern = re.compile(
        r"[,;:!?](?=[A-Za-z])"
    )

    extra_space_pattern = re.compile(
        r"(?<=\S) {2,}(?=\S)"
    )

    repeated_word_pattern = re.compile(
        r"\b(\w+)(\s+\1\b)+",
        re.IGNORECASE
    )

    # Common abbreviations to ignore
    abbreviations = [
        "e.g.", "i.e.", "et al.", "Dr.", "Mr.",
        "Ms.", "Prof.", "vs.", "Fig.", "Eq."
    ]

    abbr_spans = []
    for abbr in abbreviations:
        for match in re.finditer(re.escape(abbr), full_text):
            abbr_spans.append((match.start(), match.end()))

    def inside_abbreviation(index):
        for start, end in abbr_spans:
            if start <= index < end:
                return True
        return False

    # --------------------------
    # Sentence Capitalization
    # --------------------------

    for match in sentence_cap_pattern.finditer(full_text):

        lowercase_index = match.start(2)
        sentence_end_index = match.start(1)

        if inside_abbreviation(sentence_end_index):
            continue

        if lowercase_index >= len(position_map):
            continue

        page, char, page_height = position_map[lowercase_index]

        issues.append({
            "type": "No capital letter after sentence",
            "page": page,
            "position": get_vertical_position(char, page_height),
            "index": lowercase_index,
            "snippet": full_text[lowercase_index]
        })

    # --------------------------
    # Missing Space After Punctuation
    # --------------------------

    for match in missing_space_pattern.finditer(full_text):

        index = match.start()

        if index >= len(position_map):
            continue

        page, char, page_height = position_map[index]

        issues.append({
            "type": "Missing space after punctuation",
            "page": page,
            "position": get_vertical_position(char, page_height),
            "index": index,
            "snippet": match.group()
        })

    # --------------------------
    # Extra Spaces
    # --------------------------

    for match in extra_space_pattern.finditer(full_text):

        index = match.start()

        if index >= len(position_map):
            continue

        page, char, page_height = position_map[index]

        issues.append({
            "type": "Extra space between words",
            "page": page,
            "position": get_vertical_position(char, page_height),
            "index": index,
            "snippet": match.group()
        })

    # --------------------------
    # Repeated Words
    # --------------------------

    for match in repeated_word_pattern.finditer(full_text):

        index = match.start()

        if index >= len(position_map):
            continue

        page, char, page_height = position_map[index]

        issues.append({
            "type": "Repeated word",
            "page": page,
            "position": get_vertical_position(char, page_height),
            "index": index,
            "snippet": match.group()
        })

    return issues


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    tool = language_tool_python.LanguageTool('en-US')
    tool.disable_spellchecking()
    tex_path = 'C:/Users/jmayhall/Downloads/masters_paper/amspaperV6.1.tex'
    with open(tex_path, encoding="utf-8") as f:
        text = f.read()

    matches = tool.check(text)

    filtered = [
        m for m in matches
        if m.rule_id != "CURRENCY"
    ]

    for match in filtered:
        print(match.message)
        print("Context:", match.context)