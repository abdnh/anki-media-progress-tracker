const AUDIO_EXTENSIONS = [
    "3gp",
    "flac",
    "m4a",
    "mp3",
    "oga",
    "ogg",
    "opus",
    "spx",
    "wav",
];

const playPyCmdPattern = /play:(\w):(\d+)/;

function transformPlayButtonsToAudioElements(questionFiles, answerFiles) {
    Array.from(document.getElementsByClassName("soundLink")).forEach(e => {
        const match = playPyCmdPattern.exec(e.onclick.toString());
        if (!match) return;
        const side = match[1];
        const soundIndex = match[2];
        const src = side === "q" ? questionFiles[soundIndex] : answerFiles[soundIndex];
        if (!src) {
            // text-to-speech sound
            return;
        }
        const components = src.split('.');
        const ext = components[components.length - 1].toLowerCase();
        if (!AUDIO_EXTENSIONS.find(e => e === ext)) {
            // video
            return;
        }
        const audio = new Audio(src);
        audio.controls = true;
        e.replaceWith(audio);
        pycmd(`media-progress-tracker:get:${src}`, fileData => {
            audio.currentTime = fileData.time;
        });
        audio.addEventListener('timeupdate', () => {
            pycmd(`media-progress-tracker:set:${src}:${audio.currentTime}`);
        });
    });
}

function playAudioFiles() {
    Array.from(document.getElementsByTagName("audio")).forEach(e => {
        e.play();
    });
}
