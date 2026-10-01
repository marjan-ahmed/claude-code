import sys
import tracemalloc
from pathlib import Path
from unittest import mock


HOOKS_DIR = Path(__file__).parents[1] / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import extensibility


def test_load_guidance_does_not_allocate_for_entire_file(tmp_path):
    guidance_path = tmp_path / "claude-security-guidance.md"
    with guidance_path.open("wb") as guidance_file:
        guidance_file.truncate(32 * 1024 * 1024)

    with mock.patch.object(
        extensibility,
        "_config_paths",
        return_value=[("Project", str(guidance_path))],
    ):
        tracemalloc.start()
        try:
            guidance = extensibility._load_guidance(str(tmp_path))
            _, peak_bytes = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()

    assert len(guidance) == extensibility.GUIDANCE_MAX_BYTES
    assert peak_bytes < 1024 * 1024


def test_load_guidance_keeps_legacy_character_truncation_for_multibyte_text(tmp_path):
    guidance_path = tmp_path / "claude-security-guidance.md"
    guidance_path.write_text("日本語" * 20_000, encoding="utf-8")

    with mock.patch.object(
        extensibility,
        "_config_paths",
        return_value=[("Project", str(guidance_path))],
    ):
        guidance = extensibility._load_guidance(str(tmp_path))

    assert len(guidance) == extensibility.GUIDANCE_MAX_BYTES
