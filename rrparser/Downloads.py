"""Discover CSV datasets on RetroRules and cache them locally."""

from html.parser import HTMLParser
from pathlib import Path
from re import fullmatch
from shutil import copyfileobj
from urllib.error import URLError
from urllib.parse import urljoin, urlsplit, parse_qs
from urllib.request import urlopen
from .Args import DEFAULT_RELEASE

DOWNLOAD_PAGE = 'https://retrorules.org/download'
RR02_URL = 'https://zenodo.org/record/5828017/files/retrorules_rr02_rp2_hs.tar.gz'
RR02_FILE = 'retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_all.csv'
RR02_CACHE_FILE = 'retrorules_rr02_rp2_hs.tar.gz'


class _DatasetLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.datasets = {}

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        url = urljoin(DOWNLOAD_PAGE, dict(attrs).get('href', ''))
        parts = urlsplit(url)
        match = fullmatch(r'/dl/v(\d+\.\d+(?:\.\d+)?)/([^/]+)/templates', parts.path)
        if (parts.netloc == 'retrorules.org' and match
                and parse_qs(parts.query).get('format') == ['csv']):
            self.datasets[match.groups()] = url


def list_retrorules():
    """Return {(release, dataset): download URL}, newest releases first."""
    parser = _DatasetLinks()
    try:
        with urlopen(DOWNLOAD_PAGE, timeout=30) as response:
            parser.feed(response.read().decode('utf-8'))
    except URLError as exc:
        raise ValueError('Cannot discover RetroRules datasets: {}'.format(exc)) from exc
    if not parser.datasets:
        raise ValueError('No CSV datasets found on {}'.format(DOWNLOAD_PAGE))
    datasets = dict(sorted(parser.datasets.items(),
                           key=lambda item: tuple(map(int, item[0][0].split('.'))),
                           reverse=True))
    datasets[('rr02', 'metanetx')] = RR02_URL
    return datasets


def _download(url, filename):
    """Cache the original download without extracting or recompressing it."""
    if filename.is_file():
        return str(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    temporary = filename.with_suffix('.part')
    try:
        with urlopen(url, timeout=30) as response, temporary.open('wb') as output:
            copyfileobj(response, output)
        temporary.replace(filename)
    except URLError as exc:
        raise ValueError('Cannot download RetroRules: {}'.format(exc)) from exc
    finally:
        if temporary.exists():
            temporary.unlink()
    return str(filename)


def _selection_error(message, datasets=None):
    if datasets is None:
        try:
            datasets = list_retrorules()
        except ValueError as exc:
            return ValueError('{}\nAvailable releases could not be retrieved: {}'.format(message, exc))
    choices = '\n'.join('{}\t{}'.format(version, name) for version, name in datasets)
    return ValueError('{}\nAvailable releases and datasets:\n{}'.format(message, choices))


def fetch_dataset(rules_dir, release=DEFAULT_RELEASE, dataset='metanetx'):
    """Reuse cached rules; resolve latest only on the first download."""
    if release == 'rr02':
        if dataset != 'metanetx':
            raise ValueError('RetroRules rr02 is only available for metanetx')
        return _download(RR02_URL, Path(rules_dir) / RR02_CACHE_FILE)
    latest = release == 'latest'
    if not latest and not fullmatch(r'\d+\.\d+(?:\.\d+)?', release):
        raise _selection_error('Invalid release {!r}; use latest, rr02 or a version such as 3.1.0'.format(release))
    if not fullmatch(r'[a-z0-9_-]+', dataset):
        raise ValueError('Invalid RetroRules dataset name')
    cache = Path(rules_dir)
    selection = cache / ('retrorules-latest-{}.txt'.format(dataset))
    if release == 'latest' and selection.is_file():
        saved = selection.read_text().strip()
        if fullmatch(r'\d+\.\d+(?:\.\d+)?', saved):
            cached = cache / ('retrorules-{}-{}.csv.gz'.format(saved, dataset))
            if cached.is_file():
                return str(cached)
    filename = cache / ('retrorules-{}-{}.csv.gz'.format(release, dataset))
    if release != 'latest' and filename.is_file():
        return str(filename)
    datasets = list_retrorules()
    if release == 'latest':
        release = next((version for version, name in datasets
                        if name == dataset and version != 'rr02'), None)
    url = datasets.get((release, dataset))
    if url is None:
        raise _selection_error('Release/dataset unavailable: {} / {}'.format(release, dataset), datasets)
    cache.mkdir(parents=True, exist_ok=True)
    filename = cache / ('retrorules-{}-{}.csv.gz'.format(release, dataset))
    _download(url, filename)
    if latest:
        selection.write_text(release)
    return str(filename)
