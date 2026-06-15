# coding=utf-8
import re
import spacy
from collections import Counter

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def remove_latex_commands(text):

    # Remove comments
    text = re.sub(r'%.*', '', text)

    # Keep only document body
    match = re.search(
        r'\\begin\{document\}(.*?)\\end\{document\}',
        text,
        re.DOTALL
    )

    if match:
        text = match.group(1)

    # Remove bibliography/references section
    bib_markers = [
        r'\\bibliography\{',
        r'\\printbibliography',
        r'\\begin\{thebibliography\}'
    ]

    for marker in bib_markers:
        m = re.search(marker, text)
        if m:
            text = text[:m.start()]
            break

    # Remove common non-prose environments
    environments = [
        "table",
        "table*",
        "equation",
        "align",
        "align*",
        "lstlisting",
        "verbatim",
        "tikzpicture"
    ]

    for env in environments:
        pattern = rf'\\begin\{{{re.escape(env)}\}}.*?\\end\{{{re.escape(env)}\}}'
        text = re.sub(pattern, ' ', text, flags=re.DOTALL)

    # Preserve section titles
    text = re.sub(r'\\section\*?\{([^}]*)\}', r' \1 ', text)
    text = re.sub(r'\\subsection\*?\{([^}]*)\}', r' \1 ', text)
    text = re.sub(r'\\subsubsection\*?\{([^}]*)\}', r' \1 ', text)

    # Remove citations
    text = re.sub(r'\\cite[a-zA-Z]*\{[^}]*\}', ' ', text)

    # Remove math
    text = re.sub(r'\$.*?\$', ' ', text)
    text = re.sub(r'\\\[.*?\\\]', ' ', text, flags=re.DOTALL)
    text = re.sub(r'\\\(.*?\\\)', ' ', text, flags=re.DOTALL)

    # Remove remaining commands
    text = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?', ' ', text)

    return re.sub(r'\s+', ' ', text).strip()


def classify_verb_tense(token):
    """
    Rough tense classification using POS and tag information.
    """

    if token.pos_ != "VERB":
        return None

    # Past tense
    if token.tag_ in ["VBD", "VBN"]:
        return "PAST"

    # Present tense
    if token.tag_ in ["VB", "VBP", "VBZ", "VBG"]:
        return "PRESENT"

    return None


def analyze_sentence(sent):
    verbs = []

    for token in sent:
        tense = classify_verb_tense(token)

        if tense:
            verbs.append({
                "word": token.text,
                "tense": tense
            })

    tense_counts = Counter(v["tense"] for v in verbs)

    return {
        "sentence": sent.text.strip(),
        "verbs": verbs,
        "counts": tense_counts
    }


def find_tense_issues(text):

    doc = nlp(text)

    sentence_data = []

    for sent in doc.sents:
        sentence_data.append(
            analyze_sentence(sent)
        )

    results = []

    global_counts = Counter()

    for s in sentence_data:
        global_counts.update(s["counts"])

    dominant_tense = None

    if global_counts:
        dominant_tense = global_counts.most_common(1)[0][0]

    # Check each sentence
    for idx, s in enumerate(sentence_data, start=1):

        tenses = set(v["tense"] for v in s["verbs"])

        # Mixed tenses within one sentence
        if len(tenses) > 1:
            results.append({
                "sentence_number": idx,
                "type": "Mixed tenses within sentence",
                "sentence": s["sentence"],
                "verbs": s["verbs"]
            })

    return results, dominant_tense


def main():
    tex_file = r"C:\Users\jmayhall\Downloads\masters_paper\amspaperV6.1.tex"

    with open(tex_file, "r", encoding="utf-8") as f:
        latex_text = f.read()

    clean_text = remove_latex_commands(latex_text)

    issues, dominant_tense = find_tense_issues(clean_text)

    print("\n" + "=" * 70)
    print("TENSE ANALYSIS REPORT")
    print("=" * 70)

    print(f"\nDominant document tense: {dominant_tense}")

    if not issues:
        print("\nNo obvious tense inconsistencies detected.")
        return

    print(f"\nPotential issues found: {len(issues)}\n")

    for i, issue in enumerate(issues, 1):
        print("-" * 70)
        print(f"Issue {i}")
        print(f"Type: {issue['type']}")
        print(f"Sentence: {issue['sentence']}")
        print(f"Sentence #{issue['sentence_number']}")

        print("Detected verbs:")
        for v in issue["verbs"]:
            print(f"   {v['word']:15s} -> {v['tense']}")

        print()


if __name__ == "__main__":
    main()