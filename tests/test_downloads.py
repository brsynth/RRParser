import gzip
import tarfile
from io import BytesIO, StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import URLError

import pandas as pd
import pytest

from rrparser import build_args_parser, list_retrorules, parse_rules
from rrparser.Downloads import fetch_dataset, RR02_FILE, RR02_URL
from rrparser.Args import DEFAULT_RULES_DIR


PAGE = b'''<a href="/dl/v3.0/rhea/templates?format=csv">CSV</a>
<a href="/dl/v3.1.0/rhea/templates?format=csv">CSV</a>
<a href="/dl/v3.1.0/rhea/templates?format=json">JSON</a>
<a href="https://zenodo.org/archive.tar.gz">Legacy</a>'''
CSV = b'''TEMPLATE_ID,SCORE,TEMPLATE,REACTIONS,RADII,ECS
RR:1,0.8,"[C,N]>>[O]",RHEA:1,1;4,1.1.1.1;2.1.1
RR:2,0.5,[O]>>[C],RHEA:2,10,
'''


def test_discovery_download_and_offline_cache():
    with TemporaryDirectory() as directory:
        with patch('rrparser.Downloads.urlopen', return_value=BytesIO(PAGE)):
            releases = list_retrorules()
            assert list(releases) == [('3.1.0', 'rhea'), ('3.0', 'rhea'), ('rr02', 'metanetx')]
            assert releases[('rr02', 'metanetx')] == RR02_URL
        with patch('rrparser.Downloads.urlopen', side_effect=[BytesIO(PAGE), BytesIO(gzip.compress(CSV))]):
            filename = fetch_dataset(directory, release='latest', dataset='rhea')
        assert gzip.decompress(Path(filename).read_bytes()) == CSV
        with patch('rrparser.Downloads.urlopen', side_effect=AssertionError('Network used')):
            assert fetch_dataset(directory, release='latest', dataset='rhea') == filename
            assert fetch_dataset(directory, '3.1.0', 'rhea') == filename
        with patch('rrparser.Downloads.urlopen', return_value=BytesIO(PAGE)):
            with pytest.raises(ValueError, match='unavailable'):
                fetch_dataset(directory, '9.0', 'rhea')
        with patch('rrparser.Downloads.urlopen', return_value=BytesIO(PAGE)):
            with pytest.raises(ValueError, match='unavailable'):
                fetch_dataset(directory, release='latest', dataset='metanetx')


def test_failed_download_does_not_pollute_cache():
    with TemporaryDirectory() as directory:
        with patch('rrparser.Downloads.urlopen', side_effect=[BytesIO(PAGE), URLError('offline')]):
            with pytest.raises(ValueError, match='Cannot download'):
                fetch_dataset(directory, release='latest', dataset='rhea')
        assert not list(Path(directory).iterdir())


def test_rr02_download_cache_and_parsing():
    rules = (Path(__file__).parent / 'data/rules.csv').read_bytes()
    archive = BytesIO()
    with tarfile.open(fileobj=archive, mode='w:gz') as tar:
        for name, data in [(RR02_FILE, rules), ('../../unwanted.txt', b'unwanted')]:
            member = tarfile.TarInfo(name)
            member.size = len(data)
            tar.addfile(member, BytesIO(data))
    archive.seek(0)
    with TemporaryDirectory() as directory:
        with patch('rrparser.Downloads.urlopen', return_value=archive) as download:
            filename = fetch_dataset(directory, 'rr02')
            download.assert_called_once_with(RR02_URL, timeout=30)
        assert filename == str(Path(directory) / RR02_FILE)
        assert Path(filename).read_bytes() == rules
        with patch('rrparser.Downloads.urlopen', side_effect=AssertionError('Network used')):
            output = parse_rules(None, rules_dir=directory, release='rr02', rule_type='retro', diameters='2')
        parsed = pd.read_csv(StringIO(output))
        assert not parsed.empty
        assert set(parsed['Rule usage']) <= {'retro', 'both'}
        assert set(parsed['Diameter']) == {2}
        assert list(Path(directory).rglob('*.txt')) == []
        with pytest.raises(ValueError, match='only available for metanetx'):
            fetch_dataset(directory, 'rr02', 'rhea')


def test_rr02_missing_csv():
    archive = BytesIO()
    with tarfile.open(fileobj=archive, mode='w:gz'):
        pass
    archive.seek(0)
    with TemporaryDirectory() as directory:
        with patch('rrparser.Downloads.urlopen', return_value=archive):
            with pytest.raises(ValueError, match='does not contain'):
                fetch_dataset(directory, 'rr02')
        assert not list(Path(directory).rglob('*.csv'))
        assert not list(Path(directory).rglob('*.part'))


def test_templates_filters_scores_and_output():
    with TemporaryDirectory() as directory:
        rules = Path(directory) / 'rules.csv.gz'
        rules.write_bytes(gzip.compress(CSV))
        scores = Path(directory) / 'scores.csv'
        scores.write_text('Rule ID,Score\nRR:1,0.9\n')
        output = parse_rules(None, rules_file=str(rules), diameters='8', ec=['1.1'],
                             scores_file=str(scores), output_format='tsv')
        parsed = pd.read_csv(StringIO(output), sep='\t')
        assert parsed['Rule ID'].tolist() == ['RR:1']
        assert parsed['Score'].tolist() == [0.9]
        assert parsed['Rule'].tolist() == ['[C,N]>>[O]']
        assert len(pd.read_csv(StringIO(parse_rules(None, rules_file=str(rules), diameters='20')))) == 1
        with pytest.raises(ValueError, match='no retro/forward'):
            parse_rules(None, rules_file=str(rules), rule_type='retro')


def test_default_release_ignores_latest_cache():
    args = build_args_parser().parse_args([])
    assert args.release == '3.1.0'
    assert args.diameters == ','.join(str(diameter) for diameter in range(0, 21, 2))
    with TemporaryDirectory() as directory:
        cache = Path(directory)
        rules = cache / 'retrorules-3.1.0-metanetx.csv.gz'
        rules.write_bytes(gzip.compress(CSV))
        (cache / 'retrorules-latest-metanetx.txt').write_text('3.0')
        (cache / 'retrorules-3.0-metanetx.csv.gz').write_bytes(b'old cache')
        with patch('rrparser.Downloads.urlopen', side_effect=AssertionError('Network used')):
            assert fetch_dataset(directory) == str(rules)
            output = parse_rules(None, rules_dir=directory)
        assert pd.read_csv(StringIO(output))['Rule ID'].tolist() == ['RR:1', 'RR:2']


def test_all_template_diameters():
    with TemporaryDirectory() as directory:
        rules = Path(directory) / 'templates.csv'
        pd.DataFrame({
            'TEMPLATE_ID': ['RR:{}'.format(radius) for radius in range(11)],
            'TEMPLATE': ['[C]>>[O]'] * 11,
            'SCORE': [1.0] * 11,
            'ECS': ['1.1.1.1'] * 11,
            'RADII': list(range(11)),
        }).to_csv(rules, index=False)
        output = parse_rules(None, rules_file=str(rules))
        assert len(pd.read_csv(StringIO(output))) == 11
        for diameter in range(0, 21, 2):
            output = parse_rules(None, rules_file=str(rules), diameters=str(diameter))
            assert pd.read_csv(StringIO(output))['Rule ID'].tolist() == ['RR:{}'.format(diameter // 2)]
        output = parse_rules(None, rules_file=str(rules), diameters='0,18,20')
        assert pd.read_csv(StringIO(output))['Rule ID'].tolist() == ['RR:0', 'RR:9', 'RR:10']
        for invalid in ['1', '3', '19', '21', '22', '-2']:
            with pytest.raises(ValueError):
                parse_rules(None, rules_file=str(rules), diameters=invalid)


def test_cache_and_filtered_output_are_separate():
    args = build_args_parser().parse_args(['--dataset', 'rhea', '--radii', '4', '-o', 'rules.csv'])
    assert args.rules_dir == DEFAULT_RULES_DIR
    assert Path(DEFAULT_RULES_DIR) == Path(__file__).resolve().parents[1] / 'rrparser' / 'cache'
    assert build_args_parser().parse_args(['--cache-dir', './shared-cache']).rules_dir == './shared-cache'
    with pytest.raises(SystemExit):
        build_args_parser().parse_args(['--radii', '4', '--diameters', '8'])
    with TemporaryDirectory() as directory:
        cache = Path(directory) / 'cache'
        output = Path(directory) / 'rules.csv'
        with patch('rrparser.Downloads.urlopen', side_effect=[BytesIO(PAGE), BytesIO(gzip.compress(CSV))]):
            assert parse_rules(str(output), rules_dir=str(cache), dataset=args.dataset,
                               radii=args.radii) is None
        source = cache / 'retrorules-3.1.0-rhea.csv.gz'
        assert gzip.decompress(source.read_bytes()) == CSV
        assert pd.read_csv(output)['Rule ID'].tolist() == ['RR:1']
        with patch('rrparser.Downloads.urlopen', side_effect=AssertionError('Network used')):
            parse_rules(str(output), rules_dir=str(cache), dataset='rhea', radii='10')
        assert pd.read_csv(output)['Rule ID'].tolist() == ['RR:2']
        assert gzip.decompress(source.read_bytes()) == CSV
        assert not (cache / 'rules.csv').exists()
        assert not (Path(directory) / source.name).exists()
        for invalid in ['-1', '11', '1.5', '']:
            with pytest.raises(ValueError, match='Radii must'):
                parse_rules(None, rules_file=str(source), radii=invalid)
