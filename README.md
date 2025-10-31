## Unpopular Science

A single LaTeX book of 50 chapters spanning mathematics, physics, computer science, chemistry, philosophy, and history. The book opens with an Introduction and a Prologue, then proceeds through all 50 chapters.

### What’s inside
- **50 chapters** in indexed folders like `01_BanachTarskiParadox`, `29_HatMonotile`, `50_Consciousness`
- Each chapter includes: `title.tex`, `summary.tex`, `historical.tex`, `main.tex`, `technical.tex` (plus optional files like `topicmap.tex`, `quote.tex`, `exercises.tex`, `imagefigure.tex`, etc.)
- The main book entry point is `main.tex`, which includes Introduction, Prologue, and all chapters

### Chapter structure (per chapter)
Each chapter is typeset in a consistent, compact layout:
1) Title page
2) Sidenote page (or blank if missing)
3) Title + Summary + (optional) Topicmap + (optional) Quote
4–8) Historical + Main content (+ optional extras)
9) Technical page (exactly one page)

Note: The layout logic (including recto/verso handling) is implemented in the `\inputstory{...}` macro in the preamble and applied to every chapter.

## Build

### Requirements
- TeX Live (with LuaLaTeX available as `lualatex`)
- Python 3.10+

Tip: Use a virtual environment before running any Python utilities.

### Setup (recommended)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Compile the whole book

To get the book, compile it with:
```bash
python3 utils/compile_realtime.py main.tex
```
- Produces `main.pdf`
- Runs two LuaLaTeX passes and prints real-time progress
- Saves logs to `compile_pass1.log`, `compile_pass2.log` (and `main.log` from LaTeX)

### Compile a subset of chapters (optional)
Generate a temporary `.tex` that contains only selected chapters, then compile that file:
```bash
python3 utils/generate_chapter_subset.py 1-5,14,29 -o main_subset.tex
python3 utils/compile_realtime.py main_subset.tex
```

### Table of contents (optional plain text)
```bash
python3 generate_toc.py
# outputs TABLE_OF_CONTENTS.txt
```

### Publish PDF as GitHub Release
To share the compiled PDF without committing it to the repository, you can publish it as a GitHub release:

```bash
./release_pdf.sh
```

This creates (or updates) a `latest` release with the current `main.pdf`. The PDF remains accessible at a stable URL:
```
https://github.com/silverdavi/unpopular-science-source/releases/download/latest/main.pdf
```

**Prerequisites (one-time setup):**
```bash
brew install gh        # Install GitHub CLI
gh auth login          # Authenticate
```

## Sample Visuals

Each chapter includes a custom visual sidenote page. Here are examples from 5 chapters:

### Chapter 01: Banach-Tarski Paradox
![Banach-Tarski Sidenote](01_BanachTarskiParadox/01_%20An%20Axiom%20of%20Your%20Choice.pdf)

**Hilbert's Hotel with Infinite Buses:** An infinite number of buses, each carrying infinitely many passengers, arrives at a hotel with countably infinite rooms. To accommodate everyone, each passenger _n_ on bus _m_ is assigned to room _(p_n)^m_, where _p_n_ is the _n_th prime number. No two passengers ever collide, since distinct prime powers are never equal.

**Banach-Tarski as a Card Game:** Imagine a deck with cards A, B, A⁻¹, B⁻¹, where you can make any pile of cards, under one rule: A and A⁻¹ cancel, B and B⁻¹ cancel (the cards disappear if they are next to one another). Each card represents a rigid rotation. Four players each take all reduced sequences beginning with a specific card, forming four disjoint point sets. By prepending rotations, these sets can be recombined to form two full copies of the sphere.

### Chapter 05: Circle and Wheel Etymology
![Indo-European Language Tree](05_CircleWheel/05_%20A%20Full%20Circle%20of%20PIE.pdf)

**Indo-European Language Family Tree:** This phylogenetic reconstruction illustrates the hierarchical relationships among Indo-European languages, flowing from Proto-Indo-European (PIE) on the left to modern languages on the right. The tree demonstrates the systematic branching described by the comparative method, where shared innovations define intermediate nodes and regular sound correspondences link ancestral forms to their descendants. The PIE root *kʷékʷlos ("wheel, circle") appears across multiple branches with predictable phonological transformations: Greek κύκλος (_kyklos_) via labiovelar to velar shift, Sanskrit चक्र (_chakra_) through labiovelar palatalization, and English "wheel" via Grimm's Law (*kʷ > hw).

### Chapter 10: Solar Fusion and Quantum Tunneling
![Solar Fusion Process](10_SolarFusionQuantumTunneling/10_%20The%20Tunnel%20at%20the%20Beginning%20of%20Light.pdf)

**Solar Fusion Process:** This diagram illustrates the _proton-proton (pp) chain_, the dominant fusion process in the Sun's core, where hydrogen nuclei (protons) fuse into helium, releasing energy. The chain converts 4 protons into 1 helium-4 nucleus, with energy carried by gamma rays, neutrinos, and kinetic energy of the particles.

**Quantum Tunneling:** Enables this entire process by allowing particles to skip energy barriers. The barrier dampens the probability wave without zeroing it. This quantum mechanical effect permits fusion to occur at the Sun's core temperature (15 million K), where classical physics predicts negligible fusion rates due to insufficient thermal energy to overcome the Coulomb barrier between protons.

### Chapter 25: Firefly Bioluminescence
![Firefly Bioluminescence Scales](25_FireflyBioluminescence/25_%20Let%20There%20Be%20Bioluminsecence.pdf)

A multi-scale visualization of firefly light production:
- **Molecular Reaction (Ångström scale):** Luciferin is enzymatically converted into luciferyl-adenylate, then oxidized into oxyluciferin, releasing a visible photon.
- **Enzyme Active Site (nanometer scale):** The luciferase enzyme forms a pocket where the reaction occurs.
- **Photocyte (1–10 μm scale):** A specialized light-producing cell with supporting organelles.
- **Cell/Tissue Cross-Section (10–100 μm scale):** Densely packed light-emitting units optimized for light output.
- **Lantern Organ (1–5 mm scale):** The firefly's lantern organ with photocytes, tracheal tubes, and reflector layers.
- **Whole Firefly (centimeter scale):** The full insect with ventral lantern exposed.
- **Population-Level Output (meter scale):** A jar of ~40 fireflies generates light equivalent to a candle.

### Chapter 27: Planetary Sky Colors
![Atmospheric Scattering and Stellar Classification](27_PlanetarySkyColors/27_%20A%20Spectrum%20of%20Skies.pdf)

**Atmospheric Filtering of Stellar Radiation:** Sunlight reaching Earth undergoes selective scattering by the atmosphere. Shorter wavelengths (blue, violet) are scattered in all directions, while longer wavelengths (red, orange) pass through more directly. This results in both the blue sky and the reddening of the sun near the horizon.

**Hertzsprung–Russell Diagram:** Stars are plotted by surface temperature (x-axis, decreasing rightward) and luminosity (y-axis, log scale). Main sequence stars form a diagonal band; giants and supergiants lie above, white dwarfs below. The Sun sits in the middle of the main sequence.

## Repository layout
```text
├── main.tex                  # Book entry point (Intro, Prologue, 50 chapters)
├── preamble.tex              # Packages, macros, layout commands
├── intro.tex, prologue.tex   # Front matter
├── utils/                    # Build and analysis utilities
│   ├── compile_realtime.py
│   ├── generate_chapter_subset.py
│   ├── analyze_chapters.py
│   └── generate_page_table.py
├── generate_toc.py           # Plain-text TOC generator
├── 01_BanachTarskiParadox/
├── 02_TopologicalInsulators/
├── ...
└── 50_Consciousness/
```

## Troubleshooting
- Activate your virtual environment first: `source venv/bin/activate`
- If LaTeX fails, inspect `compile_pass1.log`, `compile_pass2.log`, and `main.log`
- Ensure `lualatex` is on your PATH (TeX Live installed)

## License
Original content © David H. Silver. All rights reserved. 