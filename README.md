Anki add-on that saves your progress on media files embedded in cards such PDFs and videos.

For PDFs, you have to link to the files in your notes (which are assumed to be in your media folder) like so:

```html
<a href="test.pdf">test.pdf</a>
```
When you review a card, the add-on will render the file inside the card,
and the last page viewed will be saved and restored in subsequent reviews.

The add-on also saves video positions, assuming you're using mpv, which is what the latest versions of Anki use by default.

## Credit

PDF rendering is provided by the [PDF.js](https://mozilla.github.io/pdf.js/) library,
licensed under the [Apache License 2.0](https://github.com/mozilla/pdf.js/blob/master/LICENSE).
