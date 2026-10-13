# ruff: noqa: N999 -- Preserve the public rrparser.Downloads import path.
"""Discover CSV datasets on RetroRules and cache them locally."""

from html.parser import HTMLParser
from pathlib import Path
from re import fullmatch
from shutil import copyfileobj
from urllib.error import URLError
from urllib.parse import parse_qs, urljoin, urlsplit
from urllib.request import urlopen

from .Args import DEFAULT_RELEASE

DOWNLOAD_PAGE = "https://retrorules.org/download"
RR02_URL = "https://zenodo.org/record/5828017/files/retrorules_rr02_rp2_hs.tar.gz"
RR02_FILE = "retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_all.csv"
RR02_CACHE_FILE = "retrorules_rr02_rp2_hs.tar.gz"


class _DatasetLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.datasets = {}

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        url = urljoin(DOWNLOAD_PAGE, dict(attrs).get("href", ""))
        parts = urlsplit(url)
        match = fullmatch(r"/dl/v(\d+\.\d+(?:\.\d+)?)/([^/]+)/templates", parts.path)
        if (
            parts.netloc == "retrorules.org"
            and match
            and parse_qs(parts.query).get("format") == ["csv"]
        ):
            self.datasets[match.groups()] = url


def list_retrorules():
    """Return {(release, dataset): download URL}, newest releases first."""
    parser = _DatasetLinks()
    try:
        with urlopen(DOWNLOAD_PAGE, timeout=30) as response:
            parser.feed(response.read().decode("utf-8"))
    except URLError as exc:
        raise ValueError(f"Cannot discover RetroRules datasets: {exc}") from exc
    if not parser.datasets:
        raise ValueError(f"No CSV datasets found on {DOWNLOAD_PAGE}")
    datasets = dict(
        sorted(
            parser.datasets.items(),
            key=lambda item: tuple(map(int, item[0][0].split("."))),
            reverse=True,
        )
    )
    datasets[("rr02", "metanetx")] = RR02_URL
    return datasets


def _download(url, filename):
    """Cache the original download without extracting or recompressing it."""
    if filename.is_file():
        return str(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    temporary = filename.with_suffix(".part")
    try:
        with urlopen(url, timeout=30) as response, temporary.open("wb") as output:
            copyfileobj(response, output)
        temporary.replace(filename)
    except URLError as exc:
        raise ValueError(f"Cannot download RetroRules: {exc}") from exc
    finally:
        if temporary.exists():
            temporary.unlink()
    return str(filename)


def _selection_error(message, datasets=None):
    if datasets is None:
        try:
            datasets = list_retrorules()
        except ValueError as exc:
            return ValueError(
                f"{message}\nAvailable releases could not be retrieved: {exc}"
            )
    choices = "\n".join(f"{version}\t{name}" for version, name in datasets)
    return ValueError(f"{message}\nAvailable releases and datasets:\n{choices}")


def fetch_dataset(
    rules_dir, release=DEFAULT_RELEASE, dataset="metanetx", available=None
):
    """Reuse cached rules; resolve latest only on the first download."""
    if release == "rr02":
        if dataset != "metanetx":
            raise ValueError("RetroRules rr02 is only available for metanetx")
        return _download(RR02_URL, Path(rules_dir) / RR02_CACHE_FILE)
    latest = release == "latest"
    if not latest and not fullmatch(r"\d+\.\d+(?:\.\d+)?", release):
        raise _selection_error(
            f"Invalid release {release!r}; use latest, rr02 or a version such as 3.1.0"
        )
    if not fullmatch(r"[a-z0-9_-]+", dataset):
        raise ValueError("Invalid RetroRules dataset name")
    cache = Path(rules_dir)
    selection = cache / (f"retrorules-latest-{dataset}.txt")
    if release == "latest" and selection.is_file():
        saved = selection.read_text().strip()
        if fullmatch(r"\d+\.\d+(?:\.\d+)?", saved):
            cached = cache / (f"retrorules-{saved}-{dataset}.csv.gz")
            if cached.is_file():
                return str(cached)
    filename = cache / (f"retrorules-{release}-{dataset}.csv.gz")
    if release != "latest" and filename.is_file():
        return str(filename)
    datasets = available if available is not None else list_retrorules()
    if release == "latest":
        release = next(
            (
                version
                for version, name in datasets
                if name == dataset and version != "rr02"
            ),
            None,
        )
    url = datasets.get((release, dataset))
    if url is None:
        raise _selection_error(
            f"Release/dataset unavailable: {release} / {dataset}", datasets
        )
    cache.mkdir(parents=True, exist_ok=True)
    filename = cache / (f"retrorules-{release}-{dataset}.csv.gz")
    _download(url, filename)
    if latest:
        selection.write_text(release)
    return str(filename)


def fetch_datasets(rules_dir, release=DEFAULT_RELEASE, dataset="metanetx"):
    """Select datasets from one release, preserving their individual caches."""
    names = sorted({name.strip() for name in dataset.replace("+", ",").split(",")})
    if any(not fullmatch(r"[a-z0-9_-]+", name) for name in names):
        raise ValueError("Use dataset names separated by commas, or all")
    if "all" in names and names != ["all"]:
        raise ValueError("Use all alone, or a list of dataset names")
    if release == "rr02" and names == ["all"]:
        names = ["metanetx"]
    if len(names) == 1 and names != ["all"]:
        return [fetch_dataset(rules_dir, release, names[0])]
    if release == "rr02":
        raise ValueError("RetroRules rr02 is only available for metanetx")
    if release != "latest" and not fullmatch(r"\d+\.\d+(?:\.\d+)?", release):
        raise _selection_error(f"Invalid release {release!r}")
    cache = Path(rules_dir)
    selection = cache / f"retrorules-selection-{release}-{'-'.join(names)}.txt"
    if selection.is_file():
        saved = selection.read_text().splitlines()
        if len(saved) == 2 and fullmatch(r"\d+\.\d+(?:\.\d+)?", saved[0]):
            selected = saved[1].split(",")
            if selected and all(fullmatch(r"[a-z0-9_-]+", name) for name in selected):
                files = [
                    cache / f"retrorules-{saved[0]}-{name}.csv.gz" for name in selected
                ]
                if (release == "latest" or release == saved[0]) and all(
                    file.is_file() for file in files
                ):
                    return list(map(str, files))
    if release != "latest" and names != ["all"]:
        files = [cache / f"retrorules-{release}-{name}.csv.gz" for name in names]
        if all(file.is_file() for file in files):
            return list(map(str, files))
    available = list_retrorules()
    versions = list(
        dict.fromkeys(version for version, _ in available if version != "rr02")
    )
    version = next(
        (
            version
            for version in versions
            if (release == "latest" or release == version)
            and (
                names == ["all"] or all((version, name) in available for name in names)
            )
        ),
        None,
    )
    if version is None:
        raise _selection_error(
            f"Release/datasets unavailable: {release} / {dataset}", available
        )
    if names == ["all"]:
        names = [name for candidate, name in available if candidate == version]
    files = [fetch_dataset(cache, version, name, available) for name in names]
    selection.write_text(version + "\n" + ",".join(names))
    return files
