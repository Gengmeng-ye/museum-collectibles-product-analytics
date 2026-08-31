import hashlib

from src.paths import EXTERNAL_RAW_DIR, RAW_DIR


def test_raw_files_match_recorded_checksums() -> None:
    checksum_file = RAW_DIR / "SHA256SUMS"
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        expected, filename = line.split(maxsplit=1)
        actual = hashlib.sha256((RAW_DIR / filename).read_bytes()).hexdigest()
        assert actual == expected


def test_external_files_match_recorded_checksums() -> None:
    checksum_file = EXTERNAL_RAW_DIR / "SHA256SUMS"
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        expected, filename = line.split(maxsplit=1)
        actual = hashlib.sha256((EXTERNAL_RAW_DIR / filename).read_bytes()).hexdigest()
        assert actual == expected
