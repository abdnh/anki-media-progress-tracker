Anki add-on that saves your progress on viewing media files embedded in cards such PDFs, audios, and videos.

For PDFs, you have to link to the files in your notes (which are assumed to be in your media folder) like so:

```html
<a href="test.pdf">test.pdf</a>
```

Anki doesn't download pasted links to PDFs automatically and leave the absolute URLs intact, which
will cause the PDF viewer to fail to load. So this add-on modifies that behavior to download
PDFs automatically to your media folder.

When you review a card, the add-on will render the file inside the card,
and the last page viewed will be saved and restored in subsequent reviews.

Audio buttons are converted by the add-on to media players with basic HTML controls and progress is saved
and restored between reviews.

The add-on also saves video positions, assuming you're using mpv, which is what the latest versions of Anki use by default.

## Known Issues

- [ ] standard Anki shortcuts to control audio don't work with audio files controlled by the add-on for now.
- [ ] HTML audio controls and progress saving don't work in the previewer and card layouts screens.

## TODO

- [ ] add option to enable audio progress saving only on some notetypes.
- [ ] make PDF downloading on paste optional?

## Credit

PDF rendering is provided by the [PDF.js](https://mozilla.github.io/pdf.js/) library,
licensed under the [Apache License 2.0](https://github.com/mozilla/pdf.js/blob/master/LICENSE).
