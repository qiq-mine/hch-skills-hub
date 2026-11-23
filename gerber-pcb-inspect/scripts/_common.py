"""Shared layer identification, input collection, and logging helpers."""
from __future__ import annotations

from contextlib import contextmanager
import logging
import re
import tempfile
from typing import Iterator
import zipfile
from pathlib import Path

EXT_ROLE = {
    "GTL": "Top Copper", "GBL": "Bottom Copper",
    "G1": "Inner Copper 1", "G2": "Inner Copper 2", "G3": "Inner Copper 3",
    "G4": "Inner Copper 4", "G5": "Inner Copper 5", "G6": "Inner Copper 6",
    "GTS": "Top Solder Mask", "GBS": "Bottom Solder Mask",
    "GTO": "Top Silkscreen", "GBO": "Bottom Silkscreen",
    "GTP": "Top Paste", "GBP": "Bottom Paste",
    "GM1": "Board Outline", "GML": "Board Outline",
    "GKO": "Keep-Out / Outline", "GM3": "Mechanical",
    "GPT": "Top Padmaster", "GPB": "Bottom Padmaster",
}

KICAD_ROLE = {
    "F_CU": "Top Copper", "B_CU": "Bottom Copper",
    "IN1_CU": "Inner Copper 1", "IN2_CU": "Inner Copper 2",
    "IN3_CU": "Inner Copper 3", "IN4_CU": "Inner Copper 4",
    "IN5_CU": "Inner Copper 5", "IN6_CU": "Inner Copper 6",
    "F_MASK": "Top Solder Mask", "B_MASK": "Bottom Solder Mask",
    "F_SILKS": "Top Silkscreen", "B_SILKS": "Bottom Silkscreen",
    "F_SILKSCREEN": "Top Silkscreen", "B_SILKSCREEN": "Bottom Silkscreen",
    "F_PASTE": "Top Paste", "B_PASTE": "Bottom Paste",
    "EDGE_CUTS": "Board Outline",
}

DRILL_EXTS = {"DRL", "TXT", "XNC", "EXC"}
NETLIST_EXTS = {"IPC", "IPCD", "NET"}
GENERIC_GERBER_EXTS = {"GBR", "GER", "ART", "PHO"}


def _is_gerber_ext(suffix: str) -> bool:
    return (
        suffix in EXT_ROLE
        or suffix in GENERIC_GERBER_EXTS
        or bool(re.fullmatch(r"G\d+", suffix))
        or bool(re.fullmatch(r"GM\d+", suffix))
    )


def identify(path: Path) -> tuple[str, str]:
    """Return (kind, role) where kind in {'gerber', 'drill', 'netlist', 'unknown'}."""
    suffix = path.suffix.lstrip(".").upper()
    if suffix in DRILL_EXTS:
        return "drill", "Drill (Excellon)"
    if suffix in NETLIST_EXTS:
        return "netlist", "IPC Netlist"
    if not _is_gerber_ext(suffix):
        return "unknown", "Unknown"

    # KiCad exports embed the layer token before the extension using '.' or '-',
    # e.g. board.F_Cu.gtl, board-F_Cu.gbr, board-Edge_Cuts.gm1.
    stem_tokens = [t for t in re.split(r"[.\-]", path.stem.upper()) if t]
    if stem_tokens and stem_tokens[-1] in KICAD_ROLE:
        return "gerber", KICAD_ROLE[stem_tokens[-1]]

    role = EXT_ROLE.get(suffix)
    if role:
        return "gerber", role
    if re.fullmatch(r"G\d+", suffix):
        return "gerber", f"Inner Copper {suffix[1:]}"
    if re.fullmatch(r"GM\d+", suffix):
        return "gerber", f"Mechanical {suffix}"
    return "gerber", "Gerber (generic)"


def _is_ignored(path: Path) -> bool:
    return "__MACOSX" in path.parts or path.name.startswith("._")


@contextmanager
def collect_inputs(target: Path, prefix: str = "gerber-inspect-") -> Iterator[list[Path]]:
    """Yield sorted input files from a directory, zip archive, or single file."""
    if target.is_file() and target.suffix.lower() == ".zip":
        with tempfile.TemporaryDirectory(prefix=prefix) as tmpdir:
            tmp = Path(tmpdir).resolve()
            with zipfile.ZipFile(target) as z:
                for info in z.infolist():
                    if info.is_dir():
                        continue
                    dest = (tmp / info.filename).resolve()
                    if not dest.is_relative_to(tmp):
                        continue
                    z.extract(info, tmp)
            yield sorted(p for p in tmp.rglob("*") if p.is_file() and not _is_ignored(p))
        return
    if target.is_file():
        yield [target]
        return
    yield sorted(p for p in target.rglob("*") if p.is_file() and not _is_ignored(p))


@contextmanager
def suppress_pygerber_warnings() -> Iterator[None]:
    """Suppress noisy 'zero surface' warnings from pygerber during rendering."""
    log = logging.getLogger()
    old_level = log.level
    log.setLevel(logging.ERROR)
    try:
        yield
    finally:
        log.setLevel(old_level)
