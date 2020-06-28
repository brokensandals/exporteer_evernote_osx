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

### Links between notes

Evernote's export functionality does not embed the note's unique identifier, or the name of the notebook to which the note belongs, into the HTML or enex files.
Also, any links between notes are exported as links into the Evernote app, rather than links between the files.

To address these limitations, you can run this tool in 'enhanced' mode:

```bash
exporteer_evernote_osx export -e TARGET_DIR
```

In this mode, the tool modifies the HTML files after export to add extra metadata fields containing the notebook name and note URL.

NOTE: This can be very slow and also bog down your computer.
I suggest exporting the notes in batches of at most a few hundred, using the `-q` parameter, and restarting the Evernote app between each batch.
Then you can combine them into one folder like this:

```bash
exporteer_evernote_osx merge TARGET_DIR FIRST_BATCH_DIR SECOND_BATCH_DIR..
```

Finally, you can replace the `evernote://` links in the HTML files with links to the corresponding exported files, by using the `relink` command:

```bash
exporteer_evernote_osx relink TARGET_DIR
```

### More documentation

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
