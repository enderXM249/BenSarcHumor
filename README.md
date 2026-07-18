# BenSarcHumor

**A Bangla-English Code-Mixed Multimodal Sarcasm Dataset**

BenSarcHumor is a multimodal (text + audio) corpus for sarcasm detection in
Bangla-English code-mixed conversational dialogue. It is drawn from two Bangla
sources centered on the same underlying narrative — a social-justice drama
based on real events — and is, to our knowledge, the first multimodal sarcasm
resource for Bangla-English code-mixing, a language pair with no prior
dedicated dataset in this line of work.

This dataset accompanies the paper *"COMICNET for Multimodal Sarcasm
Detection from Code-Mixed Language"*. If you use BenSarcHumor, please cite
that paper (see [Citation](#citation) below).

## Contents

- [Sources](#sources)
- [Statistics](#statistics)
- [Data Format](#data-format)
- [Repository Structure](#repository-structure)
- [Audio Access](#audio-access)
- [Collection & Annotation](#collection--annotation)
- [Loading the Dataset](#loading-the-dataset)
- [Known Limitations](#known-limitations)
- [License & Usage](#license--usage)
- [Citation](#citation)
- [Contact](#contact)

## Sources

| Source | Type | Utterances | Sarcastic | Speakers |
|---|---|---|---|---|
| *Proloy* (2013) | Feature film (~2h runtime, no episodes) | 509 | 127 (25.0%) | 166 |
| *Ebar Proloy* (2023) | Web series (7 of 10 released episodes annotated) | 763 | 111 (14.5%) | 365 |
| **Combined** | | **1,272** | **238 (18.7%)** | **522** |

The two sources share a continuous narrative, and the difference in sarcasm
rate between them (25.0% in the film vs. 14.5% in the series) reflects a
genuine difference in dramatic format rather than an annotation artifact.

## Statistics

| Statistic | Value |
|---|---|
| Total labeled utterances | 1,272 |
| Sarcastic / Non-sarcastic | 238 (18.7%) / 1,034 (81.3%) |
| Unique speakers | 522 |
| Mean utterance length | 19.6 words (111.5 characters) |
| Vocabulary size (word types) | 5,353 |
| Utterances with dialogue context | 1,252 (98.4%) |
| Audio coverage | 1,272 / 1,272 (100%) |
| Mean / median clip duration | 9.2s / 7.3s |
| Audio sampling rate (as recorded) | 44.1 kHz |
| Annotation team size | 5 |

## Data Format

Text, labels, and timestamps are provided as CSV files, one per source:

- `BenSarcHumor_Dataset_-_Sheet1.csv` — *Proloy* (2013)
- `BenSarcHumor_Dataset_-_Sheet2.csv` — *Ebar Proloy* (2023)

| Column | Description |
|---|---|
| `Episode` | Episode identifier (`Sheet2` only; blank/single value for the film) |
| `Speaker` | Speaker name or role, as annotated |
| `Dialogue` | Utterance text, Romanized Bangla-English code-mixed |
| `Eng_Translation` | English gloss of the utterance (annotator-provided, not a certified translation) |
| `Start_Time` / `End_Time` | Timestamp of the utterance in the source video |
| `Sarcasm_Label` | `1` = sarcastic, `0` = non-sarcastic. Rows with no label are non-dialogue markers (scene/chapter titles) and should be excluded from training |
| `Audio_Clip` | Filename of the corresponding audio segment |

A small number of rows have no `Sarcasm_Label` and no real `Dialogue` — these
are scene-transition markers in the source annotation (e.g. place names,
time-skip captions like "Koyek bochor age" / "a few years later") and are not
utterances. They should be filtered out and used only to reset dialogue
context across scene boundaries; see `load_bensarchumor.py` for a reference
implementation.

## Repository Structure

```
BenSarcHumor/
├── README.md
├── data/
│   ├── BenSarcHumor_Dataset_-_Sheet1.csv   # Proloy (2013)
│   └── BenSarcHumor_Dataset_-_Sheet2.csv   # Ebar Proloy (2023)
├── load_bensarchumor.py                    # Reference loader (cleans, unifies, builds context)
└── LICENSE
```

## Audio Access

BenSarcHumor's underlying audio-visual source material is copyrighted
broadcast and theatrical content; we do not hold distribution rights to it.
Consistent with prior multimodal sarcasm corpora built from similarly sourced
television and film content (MUStARD, MaSaC — see [Citation](#citation)):

- **Text, labels, timestamps, and speaker annotations** (this repository) are
  released openly for research use.
- **Raw audio clips** are not redistributed directly in this repository.
  [Describe your actual access mechanism here before publishing — e.g. "available
  on request for research use, contact the corresponding author" or a link to
  a gated folder, matching whatever you and your institution's research
  office settled on.]

If you extract your own audio features (MFCC, Mel-spectrogram, prosodic
statistics) from independently sourced copies of the source material, the
`Audio_Clip` filenames and `Start_Time`/`End_Time` columns are sufficient to
align them with the labeled text.

## Collection & Annotation

Utterance boundaries were manually timestamped against the source video by a
team of five annotators, who transcribed each utterance in Romanized Bangla
(the script convention common in Bangla social media and code-mixed NLP
resources), provided an English gloss, and assigned a binary sarcasm label.

## Loading the Dataset

`load_bensarchumor.py` is a reference Python loader that:
- Cleans both sheets (strips embedded newlines from merged-cell exports, drops
  scene-marker rows)
- Builds a `context` column from the preceding utterance within the same
  scene/episode, resetting context at scene and episode boundaries
- Produces a unified DataFrame with columns `dataset`, `id`, `speaker`,
  `utterance`, `context`, `text`, `label`, `episode`, `audio_clip`,
  `start_time`, `end_time`, `global_id`

```bash
python load_bensarchumor.py \
  --sheet1 data/BenSarcHumor_Dataset_-_Sheet1.csv \
  --sheet2 data/BenSarcHumor_Dataset_-_Sheet2.csv \
  --out bensarchumor_unified.csv
```

## Known Limitations

- **Episode coverage.** *Ebar Proloy* (2023) has 10 released episodes; only 7
  are annotated in this release. [State whether this is the final scope or
  annotation is ongoing.]
- **Inter-annotator agreement** across the five-person annotation team has not
  yet been computed and reported.
- **Language-composition tags** used in downstream analysis (e.g.
  English-dominant / Bangla-dominant / Code-mixed) are typically derived from
  a dictionary-collision heuristic on the Romanized text, not a validated
  language-identification model, and should be treated as approximate if you
  see them used in derived work.
- **`Eng_Translation` glosses** are annotator-provided readings of the source
  dialogue, not professionally verified translations.

## License & Usage

The transcriptions, labels, and annotations in this repository are released
for **non-commercial research use**. [Finalize and state your actual license
here — e.g. CC BY-NC 4.0 — before making the repository public; see the
Audio Access section above for the corresponding audio-specific terms.] This
repository does not grant any rights to the underlying copyrighted film and
television content from which it was derived.

## Citation

If you use BenSarcHumor, please cite:

```bibtex
@article{maity_comicnet,
  title   = {COMICNET for Multimodal Sarcasm Detection from Code-Mixed Language},
  author  = {Maity, Arpan and Chakraborty, Debashis},
  journal = {[Journal name once accepted]},
  year    = {2026}
}
```

Please also cite MUStARD and MaSaC if you use the cross-dataset experiments
or baselines reported alongside BenSarcHumor:

```bibtex
@inproceedings{castro2019mustard,
  title     = {Towards Multimodal Sarcasm Detection (An \_Obviously\_ Perfect Paper)},
  author    = {Castro, Santiago and Hazarika, Devamanyu and P{\'e}rez-Rosas, Ver{\'o}nica and Zimmermann, Roger and Mihalcea, Rada and Poria, Soujanya},
  booktitle = {ACL},
  year      = {2019}
}

@article{bedi2021multimodal,
  title   = {Multi-modal Sarcasm Detection and Humor Classification in Code-mixed Conversations},
  author  = {Bedi, Manjot and Kumar, Shivani and Akhtar, Md Shad and Chakraborty, Tanmoy},
  journal = {IEEE Transactions on Affective Computing},
  year    = {2021}
}
```

## Contact

For questions, access requests, or to report issues with the dataset, open a
GitHub issue on this repository or contact:

**Arpan Maity** — rajmaity185@gmail.com — [@enderXM249](https://github.com/enderXM249)
