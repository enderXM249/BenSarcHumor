#!/usr/bin/env python3
"""Convert the BenSarcHumor Bangla-English code-mixed sarcasm sheets into the
unified schema expected by train_comicnet.py / train_comicnet_full.py.

Usage (standalone, to inspect/export a clean CSV):
    python load_bensarchumor.py --sheet1 BenSarcHumor_Dataset_-_Sheet1.csv \
                                 --sheet2 BenSarcHumor_Dataset_-_Sheet2.csv \
                                 --out bensarchumor_unified.csv

To wire into train_comicnet.py: drop this file next to it and add, inside
load_datasets():

    if "bensarchumor" in selected:
        from load_bensarchumor import load_bensarchumor
        frames.append(load_bensarchumor(DATA_ROOT / "bensarchumor"))

and add "bensarchumor" to whatever set/list your --datasets CLI arg parses
into (check configure_from_args).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

# Columns we don't need from the raw sheets (Google Sheets export junk:
# blank leading column, stray "Unnamed" cols, duplicate end_time col).
DROP_COLS = {"Unnamed: 7", "Unnamed: 8", "end_time", " "}


def _clean_text(value: object) -> str:
    """Collapse embedded newlines/extra whitespace from merged Sheets cells."""
    if pd.isna(value):
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _clean_audio_name(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _load_sheet(path: Path, has_episode_col: bool) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors="ignore")

    if has_episode_col:
        # Episode is only populated on the first row of each block in the
        # Sheets export (merged cell) -> forward-fill.
        df["Episode"] = df["Episode"].ffill()
    else:
        df["Episode"] = "E0"

    df["Speaker"] = df["Speaker"].apply(_clean_text)
    df["Dialogue"] = df["Dialogue"].apply(_clean_text)
    df["Eng_Translation"] = df["Eng_Translation"].apply(_clean_text)
    df["Audio_Clip"] = df["Audio_Clip"].apply(_clean_audio_name)

    # Rows with no Sarcasm_Label are scene/chapter-title markers (place
    # names, segment titles), not real dialogue -- e.g. "Barrackpore",
    # "Koyek bochor age" ("a few years ago"). Flag them so we can reset
    # context across them, then drop from the final training set.
    df["is_marker"] = df["Sarcasm_Label"].isna() | (df["Dialogue"] == "")

    return df


def _build_context_and_ids(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    rows = []
    prev_dialogue = ""
    prev_episode = None
    seen_ids: dict[str, int] = {}

    for _, row in df.iterrows():
        episode = row["Episode"]
        if episode != prev_episode:
            prev_dialogue = ""  # reset context at episode boundary
            prev_episode = episode

        if row["is_marker"]:
            prev_dialogue = ""  # reset context at scene/chapter break
            continue

        label = row["Sarcasm_Label"]
        if pd.isna(label):
            continue
        try:
            label = int(float(label))
        except (ValueError, TypeError):
            continue
        if label not in (0, 1):
            continue

        utterance = row["Dialogue"]
        if not utterance:
            continue

        audio = row["Audio_Clip"]
        base_id = Path(audio).stem if audio else f"{episode}_{len(rows)}"
        uid = f"{episode}_{base_id}"
        # Disambiguate duplicate audio filenames within the sheet.
        if uid in seen_ids:
            seen_ids[uid] += 1
            uid = f"{uid}_{seen_ids[uid]}"
        else:
            seen_ids[uid] = 0

        context = prev_dialogue
        text = f"{context} [SEP] {utterance}".strip() if context else utterance

        rows.append(
            dict(
                dataset=dataset_name,
                id=uid,
                speaker=row["Speaker"],
                utterance=utterance,
                context=context,
                text=text,
                label=label,
                language_group="Bengali-English code-mixed",
                episode=episode,
                audio_clip=audio,
                start_time=row.get("Start_Time", ""),
                end_time=row.get("End_Time", ""),
            )
        )
        prev_dialogue = utterance

    return pd.DataFrame(rows)


def load_bensarchumor(
    data_dir: Path | None = None,
    sheet1_path: Path | None = None,
    sheet2_path: Path | None = None,
    dataset_name: str = "BenSarcHumor",
) -> pd.DataFrame:
    """Return the unified BenSarcHumor DataFrame.

    Either pass data_dir (containing the two default-named CSVs) or the two
    explicit paths.
    """
    if sheet1_path is None:
        sheet1_path = data_dir / "BenSarcHumor_Dataset_-_Sheet1.csv"
    if sheet2_path is None:
        sheet2_path = data_dir / "BenSarcHumor_Dataset_-_Sheet2.csv"

    frames = []
    if Path(sheet1_path).exists():
        s1 = _load_sheet(Path(sheet1_path), has_episode_col=False)
        frames.append(_build_context_and_ids(s1, dataset_name))
    else:
        print(f"BenSarcHumor sheet1 not found: {sheet1_path}")

    if Path(sheet2_path).exists():
        s2 = _load_sheet(Path(sheet2_path), has_episode_col=True)
        frames.append(_build_context_and_ids(s2, dataset_name))
    else:
        print(f"BenSarcHumor sheet2 not found: {sheet2_path}")

    if not frames:
        raise RuntimeError("No BenSarcHumor sheets found/loaded.")

    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(subset=["id"]).reset_index(drop=True)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean and unify BenSarcHumor sheets.")
    parser.add_argument("--sheet1", type=Path, required=True)
    parser.add_argument("--sheet2", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("bensarchumor_unified.csv"))
    args = parser.parse_args()

    df = load_bensarchumor(sheet1_path=args.sheet1, sheet2_path=args.sheet2)
    df.to_csv(args.out, index=False)

    print(f"Rows: {len(df)}")
    print(f"Sarcastic: {int(df.label.sum())} ({df.label.mean():.1%})")
    print(f"Episodes: {df.episode.nunique()}")
    print(f"Unique speakers: {df.speaker.nunique()}")
    print(f"Saved: {args.out}")


if __name__ == "__main__":
    main()
