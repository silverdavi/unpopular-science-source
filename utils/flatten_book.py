#!/usr/bin/env python3
"""
Flatten the LaTeX book into a single TeX file with inlined chapter content.

- Parses main.tex for chapter order using \chapterwithsummaryfromfile{<dir>} lines
- Reproduces the layout used by \inputstory{...} for each chapter
- Inlines chapter files (title, summary, sidenote, historical, main, technical, and optional extras)
- Preserves front matter and inlines intro/prologue/titlepage

Usage:
  python3 utils/flatten_book.py main.tex -o main_flat.tex
"""

import argparse
import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict

ROOT = Path(__file__).resolve().parents[1]


class ChapterRef:
    def __init__(self, label: Optional[str], directory: str, line_index: int) -> None:
        self.label = label
        self.directory = directory
        self.line_index = line_index


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except Exception:
        return ""


def read_first_nonempty_line(path: Path) -> str:
    try:
        with path.open('r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                # Skip pure comments and empty lines
                if not line or line.startswith('%'):
                    continue
                return line
    except Exception:
        pass
    return ""


def parse_main_for_chapters(main_tex_path: Path) -> Tuple[List[str], List[ChapterRef]]:
    """Return (header_lines_before_first_chapter, chapters[]) in file order.
    header_lines include everything up to but not including the first
    un-commented \chapterwithsummaryfromfile line.
    """
    lines = main_tex_path.read_text(encoding='utf-8').splitlines()

    chapters: List[ChapterRef] = []
    first_chapter_idx: Optional[int] = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('%'):
            continue
        if "\\chapterwithsummaryfromfile" in line:
            if first_chapter_idx is None:
                first_chapter_idx = i
            # Example: \chapterwithsummaryfromfile[ch:banach]{01_BanachTarskiParadox}
            m = re.search(r"\\chapterwithsummaryfromfile(?:\[([^\]]+)\])?\{([^\}]+)\}", line)
            if m:
                label = m.group(1)
                directory = m.group(2)
                chapters.append(ChapterRef(label=label, directory=directory, line_index=i))

    header_lines = lines[: (first_chapter_idx if first_chapter_idx is not None else len(lines))]
    return header_lines, chapters


def inline_if_root_input(line: str) -> Optional[str]:
    """If the line is an \input{<name>} in the repository root for known front-matter
    files, return the inlined content; otherwise None.
    We inline: intro, prologue, titlepage. We do NOT inline preamble.
    """
    m = re.match(r"^\\input\{([^\}]+)\}\s*$", line.strip())
    if not m:
        return None
    name = m.group(1)
    if name in {"preamble"}:
        return None
    if name in {"intro", "prologue", "titlepage"}:
        path = ROOT / f"{name}.tex"
        content = read_text_file(path)
        if content:
            return f"% BEGIN INLINE {name}.tex\n" + content.rstrip() + f"\n% END INLINE {name}.tex"
    return None


def build_title_page_block(title_tex: str) -> str:
    return """
% --- PAGE 1: Dedicated Title Page (big, centered) ---
\thispagestyle{empty}
\begin{center}
    \vspace*{\fill}
    {\fontsize{48pt}{62pt}\selectfont\bfseries\raggedright
    \parbox{0.8\textwidth}{\centering
""".rstrip('\n') + "\n" + title_tex.rstrip('\n') + "\n" + """
    }}
    \vspace*{\fill}
\end{center}
\clearpage
""".lstrip('\n')


def build_page3_intro_block(title_tex: str, summary_tex: str, topicmap_tex: str, quote_tex: str) -> str:
    body = []
    body.append("% --- PAGE 3: Title + Summary + Topicmap + Quote ---")
    body.append("\\thispagestyle{empty}")
    body.append("\\begin{center}")
    body.append("    \\vspace*{\\fill}")
    body.append("    {\\Huge \\bfseries ")
    body.append(title_tex.rstrip())
    body.append("    }")
    body.append("")
    body.append("    \\vspace{2em}")
    body.append("    \\begin{minipage}{0.8\\textwidth}")
    body.append("        {\\fontsize{13pt}{18pt}\\selectfont\\color{black}")
    body.append("        \\justifying")
    body.append(summary_tex.rstrip())
    body.append("        }")
    body.append("    \\end{minipage}")
    body.append("")
    body.append("    \\vspace{2em}")
    body.append("    \\chapterseparator")
    body.append("    \\vspace{2em}")
    if topicmap_tex:
        body.append("    \\begin{minipage}{0.7\\textwidth}")
        body.append("        \\centering")
        body.append(topicmap_tex.rstrip())
        body.append("    \\end{minipage}")
    body.append("    \\vfill")
    if quote_tex:
        body.append("    \\vspace{2em}")
        body.append("    \\begin{minipage}{0.8\\textwidth}")
        body.append("        \\centering \\itshape")
        body.append(quote_tex.rstrip())
        body.append("    \\end{minipage}")
    body.append("    \\vspace*{\\fill}")
    body.append("\\end{center}")
    body.append("\\clearpage")
    return "\n".join(body) + "\n"


def inline_tex_file(path: Path) -> str:
    content = read_text_file(path)
    return (f"% BEGIN INLINE {path.relative_to(ROOT)}\n" + content.rstrip() +
            f"\n% END INLINE {path.relative_to(ROOT)}\n") if content else ""


def generate_flattened(main_tex_path: Path, output_path: Path) -> None:
    header_lines, chapters = parse_main_for_chapters(main_tex_path)

    # Compose header, inlining intro/prologue/titlepage where encountered
    output: List[str] = []
    output.append("% === FLATTENED BOOK GENERATED BY utils/flatten_book.py ===")
    for line in header_lines:
        maybe_inline = inline_if_root_input(line)
        output.append(maybe_inline if maybe_inline is not None else line)

    # Ensure we are in main matter after front-matter, as in original main.tex
    # The header_lines already include up to \mainmatter; no changes here.

    # Process each chapter in the original order
    for ch in sorted(chapters, key=lambda c: c.line_index):
        chapter_dir = ROOT / ch.directory
        title_path = chapter_dir / 'title.tex'
        summary_path = chapter_dir / 'summary.tex'
        sidenote_path = chapter_dir / 'sidenote.tex'
        historical_path = chapter_dir / 'historical.tex'
        main_path = chapter_dir / 'main.tex'
        technical_path = chapter_dir / 'technical.tex'
        topicmap_path = chapter_dir / 'topicmap.tex'
        quote_path = chapter_dir / 'quote.tex'
        phenomenon_extra_path = chapter_dir / 'phenomenon_extra.tex'
        joke_path = chapter_dir / 'joke.tex'
        exercises_path = chapter_dir / 'exercises.tex'
        cartoon_path = chapter_dir / 'cartoon.tex'
        imagefigure_path = chapter_dir / 'imagefigure.tex'

        title_first = read_first_nonempty_line(title_path)
        summary_first = read_first_nonempty_line(summary_path)

        title_tex = inline_tex_file(title_path)
        summary_tex = inline_tex_file(summary_path)
        topicmap_tex = read_text_file(topicmap_path)
        quote_tex = read_text_file(quote_path)

        output.append("")
        output.append(f"% ===== CHAPTER {ch.directory} =====")
        output.append("\\refstepcounter{chapter}")
        if ch.label:
            output.append(f"\\label{{{ch.label}}}")
        output.append("\\phantomsection")

        # Verso empty page BEFORE each chapter (as in inputstory)
        output.append("% --- Verso empty page before chapter ---")
        output.append("\\clearpage")
        output.append("\\thispagestyle{empty}")
        output.append("\\mbox{}")
        output.append("\\clearpage")

        # Page 1: Big Title
        output.append(build_title_page_block(title_tex))

        # Page 2: Sidenote or empty
        output.append("% --- PAGE 2: Sidenote (or empty) ---")
        if sidenote_path.exists():
            output.append(inline_tex_file(sidenote_path))
        else:
            output.append("\\thispagestyle{empty}")
            output.append("\\mbox{}")
        output.append("\\clearpage")

        # Add TOC entry here (after sidenote page)
        output.append("% --- Table of Contents entry (title + summary first lines) ---")
        output.append("\\addcontentsline{toc}{chapter}{%")
        output.append(f"  \\protect\\numberline{{\\thechapter}}{title_first}\\\\")
        output.append(f"  {{\\normalfont\\small\\textit{{\\textcolor{{summarycolor}}{{{summary_first}}}}}}}%")
        output.append("}")
        output.append("\\clearpage")

        # Page 3: Title + Summary + Topicmap + Quote
        output.append(build_page3_intro_block(title_tex, summary_tex, topicmap_tex, quote_tex))

        # Pages 4-8: Historical + Main + Optional materials
        output.append("% --- PAGES 4-8: Historical + Main + Optional ---")
        output.append(f"\\chaptermark{{{title_first}}}")
        output.append("{\\LARGE \\bfseries ")
        output.append(title_tex.rstrip())
        output.append("}")
        output.append(inline_tex_file(historical_path))
        output.append(inline_tex_file(main_path))
        if phenomenon_extra_path.exists():
            output.append(inline_tex_file(phenomenon_extra_path))
        if joke_path.exists():
            output.append(inline_tex_file(joke_path))
        if exercises_path.exists():
            output.append(inline_tex_file(exercises_path))
        if cartoon_path.exists():
            output.append(inline_tex_file(cartoon_path))
        if imagefigure_path.exists():
            output.append(inline_tex_file(imagefigure_path))

        # Page 9: Technical (exactly one page)
        output.append("% --- PAGE 9: Technical ---")
        output.append("\\newpage")
        output.append(inline_tex_file(technical_path))

    # End document
    output.append("\\end{document}")

    # Write to output
    output_path.write_text("\n".join(output) + "\n", encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description='Flatten LaTeX book into a single TeX file with inlined chapter content')
    parser.add_argument('main_tex', help='Path to main.tex (entry point)')
    parser.add_argument('-o', '--output', default='main_flat.tex', help='Output TeX filename (default: main_flat.tex)')
    args = parser.parse_args()

    main_tex_path = Path(args.main_tex).resolve()
    if not main_tex_path.exists():
        raise SystemExit(f"ERROR: {main_tex_path} not found")

    output_path = (Path.cwd() / args.output).resolve()
    generate_flattened(main_tex_path, output_path)
    print(f"✅ Flattened TeX written: {output_path}")


if __name__ == '__main__':
    main()
