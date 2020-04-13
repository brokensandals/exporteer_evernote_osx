from pathlib import Path
from tempfile import TemporaryDirectory
from exporteer_evernote_osx import cli


# I don't know of a good way to actually test that the sync commands
# work, but we can at least test that they run without crashing.

def test_sync():
    assert cli.main(['sync']) == 0


def test_sync_immediate():
    assert cli.main(['sync', '-i']) == 0


def test_sync_time_options():
    assert cli.main(['sync', '-d', '5', '-t', '10']) in [0, 2]


def test_list_notebooks(capsys):
    assert cli.main(['notebooks']) == 0
    cap = capsys.readouterr()
    assert len(cap.out.splitlines()) > 1


def test_export_enex():
    with TemporaryDirectory() as rawpath:
        path = Path(rawpath).joinpath('test.enex').resolve()
        assert cli.main(['export', str(path), '-Eq', 'created:month']) == 0
        assert path.stat().st_size > 100


def test_export_enex_by_notebook():
    with TemporaryDirectory() as rawpath:
        path = Path(rawpath).joinpath('test').resolve()
        assert cli.main(['export', str(path), '-Enq', 'created:month']) == 0
        assert path.is_dir()
        files = list(path.glob('*.enex'))
        assert len(files) > 1
        assert files[0].stat().st_size > 100


def test_export_html():
    with TemporaryDirectory() as rawpath:
        path = Path(rawpath).joinpath('test').resolve()
        assert cli.main(['export', str(path), '-q', 'created:month']) == 0
        assert path.is_dir()
        assert len(list(path.glob('*.html'))) > 0


def test_export_html_by_notebook():
    with TemporaryDirectory() as rawpath:
        path = Path(rawpath).joinpath('test').resolve()
        assert cli.main(['export', str(path), '-nq', 'created:month']) == 0
        assert path.is_dir()
        assert len(list(path.glob('*/'))) > 1
        assert len(list(path.glob('*/*.html'))) > 1


def test_export_no_matches():
    with TemporaryDirectory() as rawpath:
        path = Path(rawpath).joinpath('test.enex').resolve()
        assert cli.main(['export', str(path), '-Eq', 'tag:totallybogustag']) == 3
