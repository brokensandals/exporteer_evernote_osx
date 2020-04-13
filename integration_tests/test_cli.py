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
