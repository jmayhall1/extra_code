# coding=utf-8
import re
import pdfplumber
import language_tool_python


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_pdf_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[\u2000-\u200A\u202F\u205F\u3000]", " ", text)
    return text


# ============================================================
# BUILD GLOBAL TEXT + POSITION MAP + CHARACTER COORDINATES
# ============================================================

def extract_pdf_with_map(pdf_path):

    full_text = []
    position_map = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):

            page_height = page.height
            chars = sorted(page.chars, key=lambda c: (c["top"], c["x0"]))

            previous_char = None

            for char in chars:

                # Insert synthetic space if gap is large
                if previous_char:
                    same_line = abs(char["top"] - previous_char["top"]) < 2

                    if same_line:
                        gap = char["x0"] - previous_char["x1"]

                        if gap > 1.5:  # spacing threshold (tune if needed)
                            full_text.append(" ")
                            position_map.append((page_number, previous_char, page_height))

                    else:
                        # New line detected
                        full_text.append("\n")
                        position_map.append((page_number, previous_char, page_height))

                full_text.append(char["text"])
                position_map.append((page_number, char, page_height))

                previous_char = char

            full_text.append("\n")
            position_map.append((page_number, None, page_height))

    full_text = normalize_pdf_text("".join(full_text))

    return full_text, position_map


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

    # pdf_path = "C:/Users/jmayhall/Downloads/masters_thesis/main.pdf"
    #
    # print("Analyzing PDF...")
    # full_text, position_map = extract_pdf_with_map(pdf_path)
    #
    # issues = check_document(full_text, position_map)
    #
    # if not issues:
    #     print("No issues found.")
    # else:
    #     for issue in issues:
    #         context = get_context(full_text, issue["index"])
    #
    #         print("=" * 80)
    #         print(f"Page {issue['page']} ({issue['position']})")
    #         print(f"Issue: {issue['type']}")
    #         print(f"Matched: '{issue['snippet']}'")
    #         print(f"Context: ...{context}...")

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