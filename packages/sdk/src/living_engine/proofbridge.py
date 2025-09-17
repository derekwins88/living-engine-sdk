"""Utilities for writing proof ledgers and capsules."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import IO, Any, Dict, Iterable

Capsule = Dict[str, Any]


class ProofBridge:
    """Persist proof capsules to both CSV and JSONL sinks."""

    def __init__(self, csv_path: Path | str, jsonl_path: Path | str):
        self._csv_path = Path(csv_path)
        self._jsonl_path = Path(jsonl_path)
        self._csv_file: IO[str] = self._csv_path.open("w", newline="", encoding="utf-8")
        self._jsonl_file: IO[str] = self._jsonl_path.open("w", encoding="utf-8")
        self._csv_writer = csv.DictWriter(
            self._csv_file,
            fieldnames=("ts", "glyph", "entropy", "verdict"),
        )
        self._csv_writer.writeheader()
        self._count = 0

    # ------------------------------------------------------------------
    def write_capsule(self, timestamp: str, capsule: Capsule) -> None:
        """Write a single capsule to both outputs."""

        row = {
            "ts": timestamp,
            "glyph": capsule.get("glyph"),
            "entropy": capsule.get("entropy"),
            "verdict": capsule.get("verdict", "OPEN"),
        }
        self._csv_writer.writerow(row)
        payload = {"ts": timestamp, **capsule}
        self._jsonl_file.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self._count += 1

    def write_many(self, entries: Iterable[tuple[str, Capsule]]) -> None:
        """Write a batch of capsules."""

        for timestamp, capsule in entries:
            self.write_capsule(timestamp, capsule)

    def stats(self) -> Dict[str, int]:
        """Return summary statistics."""

        return {"capsules_written": self._count}

    # ------------------------------------------------------------------
    def close(self) -> None:
        self._csv_file.close()
        self._jsonl_file.close()

    def __enter__(self) -> "ProofBridge":  # pragma: no cover - trivial
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - trivial
        self.close()


def sha256_file(path: Path | str) -> str:
    """Compute the SHA-256 digest of a file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


__all__ = ["ProofBridge", "sha256_file"]
