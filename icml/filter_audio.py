#!/usr/bin/env python3
"""
从 ICML 2026 录用论文中筛选语音/音频/音乐相关论文。
"""

import json
from pathlib import Path

INPUT_PATH = Path("data/icml2026_accepted.json")
OUTPUT_PATH = Path("data/icml2026_audio_papers.json")

KEYWORDS = [
    "speech", "speaker", "asr", "automatic speech recognition",
    "text-to-speech", "tts", "voice", "vocal", "dialogue",
    "spoken language", "prosody", "phoneme", "phonetic",
    "audio", "sound", "acoustic", "waveform", "wave",
    "music", "musical", "song", "singing", "melody",
    "binaural", "spatial audio", "audio generation",
    "audio synthesis", "audio super-resolution",
    "neural audio", "audio codec", "audio compression",
    "signal processing", "spectrogram", "stft", "mfcc",
    "wav2vec", "whisper", "hubert", "wavlm",
]


def matches_audio(text: str) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in KEYWORDS)


def main():
    if not INPUT_PATH.exists():
        print(f"Input not found: {INPUT_PATH}")
        print("请先运行: python scraper.py")
        return

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        papers = json.load(f)

    audio_papers = []
    for p in papers:
        combined = " ".join(filter(None, [
            p.get("title", ""),
            p.get("abstract", ""),
            str(p.get("keywords", "")),
            p.get("primary_area", ""),
        ]))
        if matches_audio(combined):
            audio_papers.append(p)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(audio_papers, f, ensure_ascii=False, indent=2)

    print(f"Total accepted:    {len(papers)}")
    print(f"Audio/Speech match: {len(audio_papers)}")
    print(f"Ratio:             {len(audio_papers)/len(papers)*100:.2f}%")
    print(f"Saved to:          {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
