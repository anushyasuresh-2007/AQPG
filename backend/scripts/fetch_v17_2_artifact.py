"""Fetch and verify the approved AQPG V17.2 model artifact for deployment."""

import hashlib
import os
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from urllib.error import URLError
from urllib.request import Request, urlopen

EXPECTED_FILES = {
    "config.json": "8175ff688ac72a8aeb00416a323fb536a51f25b3e4b28eea48ab9efaee3047cd",
    "generation_config.json": "196b3297c73e8b686aa1c3bc1fe99b17362ddd682354a710a6f07c697eb6e273",
    "model.safetensors": "e2cfed7ba5fd44ea31c67e352985e42072fb6532ce96222769b573530d3b4954",
    "special_tokens_map.json": "65d84a9271d68f1230ab99518c00f0f7eaef95c7b363001595ba6fa662d434b1",
    "tokenizer.json": "8c3804f01b141a4f28649b2ff899f7eb3bedad28fd898f8c38b7dbc70db700bf",
    "tokenizer_config.json": "ebc3fede7a53346b49346d8e8fbb7d664b9b448f559660c36195bb19e2d5eaaa",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


def download_artifact(destination: Path) -> None:
    artifact_url = required_environment("V17_2_ARTIFACT_URL")
    request = Request(artifact_url, headers={"User-Agent": "AQPG-V17.2-deployer"})
    token = os.environ.get("V17_2_ARTIFACT_TOKEN", "").strip()
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urlopen(request, timeout=300) as response, destination.open("wb") as output:
            shutil.copyfileobj(response, output)
    except (OSError, URLError):
        raise RuntimeError("V17.2 artifact download failed") from None


def safe_extract(archive_path: Path, destination: Path) -> None:
    try:
        archive = tarfile.open(archive_path, mode="r:gz")
    except (OSError, tarfile.TarError):
        raise RuntimeError("V17.2 artifact archive could not be opened") from None

    with archive:
        root = destination.resolve()
        for member in archive.getmembers():
            parts = PurePosixPath(member.name).parts
            if not parts or member.name.startswith("/") or ".." in parts:
                raise RuntimeError("V17.2 artifact contains an unsafe path")
            target = (destination.joinpath(*parts)).resolve()
            if root != target and root not in target.parents:
                raise RuntimeError("V17.2 artifact contains an unsafe path")
            if member.issym() or member.islnk() or not (member.isdir() or member.isfile()):
                raise RuntimeError("V17.2 artifact contains an unsupported archive entry")

            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError("V17.2 artifact contains an unreadable file")
            target.parent.mkdir(parents=True, exist_ok=True)
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def verify_staged_checkpoint(checkpoint: Path) -> None:
    if not checkpoint.is_dir():
        raise RuntimeError("V17.2 artifact does not contain best_model/")

    actual_files = {path.name for path in checkpoint.iterdir() if path.is_file()}
    if actual_files != set(EXPECTED_FILES):
        raise RuntimeError("V17.2 artifact file set does not match the approved checkpoint")

    for filename, expected_hash in EXPECTED_FILES.items():
        actual_hash = sha256_file(checkpoint / filename)
        if actual_hash != expected_hash:
            raise RuntimeError(f"V17.2 artifact hash verification failed for {filename}")


def install_artifact(staged_checkpoint: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for filename in EXPECTED_FILES:
        shutil.copy2(staged_checkpoint / filename, target / filename)


def main() -> int:
    backend_root = Path(__file__).resolve().parents[1]
    target = backend_root / "ml" / "models" / "checkpoints" / "flan_t5_v17_2" / "best_model"
    expected_archive_hash = required_environment("V17_2_ARTIFACT_ARCHIVE_SHA256").lower()
    if len(expected_archive_hash) != 64 or any(char not in "0123456789abcdef" for char in expected_archive_hash):
        raise RuntimeError("V17_2_ARTIFACT_ARCHIVE_SHA256 must be a SHA-256 hex digest")

    with tempfile.TemporaryDirectory(prefix="aqpg-v17-2-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        archive_path = temporary_root / "v17_2_artifact.tar.gz"
        download_artifact(archive_path)
        if sha256_file(archive_path) != expected_archive_hash:
            raise RuntimeError("V17.2 artifact archive hash verification failed")

        extracted_root = temporary_root / "extracted"
        extracted_root.mkdir()
        safe_extract(archive_path, extracted_root)
        staged_checkpoint = extracted_root / "best_model"
        verify_staged_checkpoint(staged_checkpoint)
        install_artifact(staged_checkpoint, target)

    verify_staged_checkpoint(target)
    print("V17.2 artifact downloaded, installed, and verified")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
