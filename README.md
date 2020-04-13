# exporteer\_evernote\_osx

This is a very simple tool for exporting data from Evernote.
It uses AppleScript to tell the Mac Evernote app to perform an export.

## Usage

Install:

1. Install python3 and pip
2. `pip3 install exporteer_evernote_osx`

Before running an export, you might wish to ensure the app has synced with the cloud:

```bash
exporteer_evernote_osx sync
```

To export all your notes to HTML files, with each notebook in a separate subdirectory:

```bash
exporteer_evernote_osx export -n TARGET_DIR
```

To export all notes matching a query (for instance, notes created this year) to an enex file:

```bash
exporteer_evernote_osx export -Eq 'created:year' TARGET_FILE.enex
```

Full command list and options can be seen in the [doc folder](doc/).

## Development

Setup:

1. Install python3 and pip
2. Clone the repo
3. I recommend creating a venv:
    ```bash
    cd exporteer_evernote_osx
    python3 -m venv venv
    source venv/bin/activate
    ```
4. Install dependencies:
    ```bash
   pip install .
   pip install -r requirements-dev.txt
    ```

To run integration tests (these assume you've created at least a couple notes this month in a couple different notebooks):

```bash
PYTHONPATH=src pytest
```

(Overriding PYTHONPATH as shown ensures the tests run against the code in the src/ directory rather than the installed copy of the package.)

To run the CLI:

```bash
PYTHONPATH=src python -m exporteer_evernote_osx ...
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/brokensandals/exporteer_evernote_osx.

## License

This is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
