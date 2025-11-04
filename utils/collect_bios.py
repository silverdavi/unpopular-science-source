#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


@dataclass
class Context:
    chapter: str
    filename: str
    sentence: str


CHAPTER_DIR_PATTERN = re.compile(r"^\d{2}_")


def iter_chapter_tex_files(root_dir: Path) -> Iterable[Path]:
    for child in sorted(root_dir.iterdir()):
        if child.is_dir() and CHAPTER_DIR_PATTERN.match(child.name):
            for tex_path in sorted(child.glob("*.tex")):
                yield tex_path


def remove_comments(text: str) -> str:
    # Remove LaTeX comments (ignore escaped %)
    return re.sub(r"(?<!\\)%.*", "", text)


def remove_math(text: str) -> str:
    # Remove display and inline math blocks
    patterns = [
        r"\$\$[\s\S]*?\$\$",   # $$ ... $$
        r"\$[^$]*\$",             # $ ... $
        r"\\\[[\s\S]*?\\\]",  # \[ ... \]
        r"\\\([\s\S]*?\\\)",   # \( ... \)
    ]
    for pat in patterns:
        text = re.sub(pat, " ", text)
    return text


def strip_commands_keep_text(text: str) -> str:
    # Replace tildes with spaces
    text = text.replace("~", " ")
    # Remove \begin{...} and \end{...}
    text = re.sub(r"\\begin\{[^{}]*\}", " ", text)
    text = re.sub(r"\\end\{[^{}]*\}", " ", text)
    # Remove command names like \textit, \cite, etc., but keep their arguments by dropping only the command token
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    # Drop braces
    text = text.replace("{", "").replace("}", "")
    # Unescape common sequences
    text = text.replace("\\%", "%").replace("\\_", "_").replace("\\&", "&")
    return text


def clean_tex(text: str) -> str:
    text = remove_comments(text)
    text = remove_math(text)
    text = strip_commands_keep_text(text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str) -> List[str]:
    # Simple sentence splitter on punctuation boundaries
    # Ensure punctuation is followed by a space
    pieces = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in pieces if s.strip()]
    return sentences


STOPWORDS = {
    # Common capitalized words that are not person names in our context
    "The", "This", "That", "These", "Those", "We", "It", "If", "In", "On", "For", "From", "By",
    "With", "As", "At", "Of", "And", "Or", "But", "When", "While", "Because", "Thus", "Hence",
    # Structural terms
    "Figure", "Section", "Table", "Appendix", "Definition", "Example", "Proof", "Remark",
    "Corollary", "Theorem", "Lemma", "Equation", "Chapter", "Sidenote", "Quote",
    # Months
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
}


SUFFIX_EXCLUDE = {
    "Paradox", "Theorem", "Rule", "Effect", "Equation", "Model", "Hypothesis", "Problem", "Experiment",
    "Conjecture", "Algorithm", "Inequality", "Attack", "Process", "Trick", "Parable", "Principle",
}


def extract_names_from_sentence(sentence: str) -> List[str]:
    # Normalize dashes to spaces to split hyphenated names
    normalized = sentence.replace("–", " ").replace("—", " ").replace("-", " ")
    # Keep only word-like tokens with letters and apostrophes
    raw_tokens = re.findall(r"[A-Za-zÀ-ÖØ-Ýà-öø-ÿ'’]+", normalized)

    def is_name_token(tok: str) -> bool:
        base = tok.rstrip("'’s")
        if not base:
            return False
        # First char uppercase handles unicode titles too
        if not base[0].isupper():
            return False
        # Exclude all-caps tokens (likely acronyms)
        if len(base) >= 2 and base.isupper():
            return False
        if base in STOPWORDS:
            return False
        return True

    names: List[str] = []
    i = 0
    n = len(raw_tokens)
    while i < n:
        if is_name_token(raw_tokens[i]):
            seq = [raw_tokens[i].rstrip("'’s")]
            j = i + 1
            # Capture up to 3-token names
            while j < n and len(seq) < 3 and is_name_token(raw_tokens[j]):
                seq.append(raw_tokens[j].rstrip("'’s"))
                j += 1
            # Filter out conceptual suffixes (e.g., "Banach Tarski Paradox")
            if seq and seq[-1] not in SUFFIX_EXCLUDE:
                candidate = " ".join(seq)
                names.append(candidate)
            i = j
        else:
            i += 1
    return names


def collect_bios(root_dir: Path, max_contexts_per_name: int = 5) -> Dict[str, List[Context]]:
    name_to_contexts: Dict[str, List[Context]] = defaultdict(list)
    for tex_path in iter_chapter_tex_files(root_dir):
        try:
            raw = tex_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        cleaned = clean_tex(raw)
        sentences = split_sentences(cleaned)
        chapter = tex_path.parent.name
        filename = tex_path.name
        for sent in sentences:
            names = extract_names_from_sentence(sent)
            if not names:
                continue
            # Deduplicate names per sentence
            for name in sorted(set(names)):
                contexts = name_to_contexts[name]
                if len(contexts) >= max_contexts_per_name:
                    continue
                contexts.append(Context(chapter=chapter, filename=filename, sentence=sent.strip()))
    return name_to_contexts


def write_bios(output_path: Path, name_to_contexts: Dict[str, List[Context]]) -> None:
    lines: List[str] = []
    lines.append(f"Bios: names and context extracted from chapters (generated {datetime.now().isoformat(timespec='seconds')})")
    lines.append("")
    for name in sorted(name_to_contexts.keys(), key=lambda s: s.lower()):
        lines.append(f"Name: {name}")
        for ctx in name_to_contexts[name]:
            snippet = ctx.sentence
            # Truncate overly long context lines for readability
            if len(snippet) > 300:
                snippet = snippet[:297].rstrip() + "..."
            lines.append(f"  - [{ctx.chapter}/{ctx.filename}] {snippet}")
        lines.append("")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: List[str]) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    glossary_dir = repo_root / "glossary_terms"
    glossary_dir.mkdir(parents=True, exist_ok=True)
    output_path = glossary_dir / "bios.txt"

    name_to_contexts = collect_bios(repo_root)
    write_bios(output_path, name_to_contexts)

    print(f"Wrote {len(name_to_contexts)} names to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


