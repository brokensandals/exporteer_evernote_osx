from pathlib import Path
import re
from tempfile import TemporaryDirectory
import pytest
from exporteer_evernote_osx import cli


def test_help(capsys):
    doc = Path('doc')
    with pytest.raises(SystemExit):
        cli.main(['-h'])
    cap = capsys.readouterr()
    doc.joinpath('usage.txt').write_text(
        cap.out.replace('pytest', 'exporteer_evernote_osx'))
    cmds = re.search('\\{(.+)\\}', cap.out).group(1)
    for cmd in cmds.split(','):
        with pytest.raises(SystemExit):
            cli.main([cmd, '-h'])
        cap = capsys.readouterr()
        doc.joinpath(f'usage-{cmd}.txt').write_text(
            cap.out.replace('pytest', 'exporteer_evernote_osx'))


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
        assert files[1].stat().st_size > 100
        assert files[0].read_text() != files[1].read_text()


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
        dirs = list(path.glob('*/'))
        assert len(dirs) > 1
        files1 = list(dirs[0].glob('*.html'))
        files2 = list(dirs[1].glob('*.html'))
        assert len(files1) > 0
        assert len(files2) > 0
        assert [f.name for f in files1] != [f.name for f in files2]


def test_export_enhanced_and_relink():
    with TemporaryDirectory() as rawpath:
        path = Path(rawpath).joinpath('test').resolve()
        assert cli.main(['export', str(path), '-eq', 'created:month']) == 0
        assert path.is_dir()
        files = list(path.glob('*.html'))
        assert len(files) > 0
        for file in files:
            text = file.read_text()
            assert '<meta name="evernote-notebook" content="' in text
            assert '<meta name="evernote-url" content="evernote:///' in text
        assert cli.main(['relink', str(path)]) == 0
        for file in files:
            text = file.read_text()
            assert '<meta name="evernote-notebook" content="' in text
            assert '<meta name="evernote-url" content="evernote:///' in text
            # Ideally I'd make the following assertion, but it doesn't
            # really work unless you're exporting all notes, which is slow.
            # assert text.count('evernote://') == 1


def test_export_no_matches():
    with TemporaryDirectory() as rawpath:
        path = Path(rawpath).joinpath('test.enex').resolve()
        assert cli.main(['export', str(path), '-Eq', 'tag:totallybogustag']) == 3
