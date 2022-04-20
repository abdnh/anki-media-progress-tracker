from typing import Any, Dict, Tuple, List
import json
from pathlib import Path

from anki.cards import Card
from aqt import mw
from aqt.qt import *
from aqt.reviewer import Reviewer
from aqt.browser.previewer import Previewer
from aqt.clayout import CardLayout
from aqt.webview import WebContent
from aqt.gui_hooks import (
    webview_will_set_content,
    card_will_show,
    webview_did_receive_js_message,
    reviewer_will_play_answer_sounds,
    reviewer_will_play_question_sounds,
)
from anki.sound import SoundOrVideoTag, AVTag
from aqt.sound import is_audio_file

from . import consts

base_path = f"/_addons/{mw.addonManager.addonFromModule(__name__)}/web"
mw.addonManager.setWebExports(__name__, r"web/.*")


def append_webcontent(webcontent: WebContent, context: Any) -> None:

    if isinstance(context, (Reviewer, Previewer, CardLayout)):
        webcontent.js.append(f"{base_path}/pdf.js")
        webcontent.js.append(f"{base_path}/audio.js")
        webcontent.css.append(f"{base_path}/pdf.css")


current_qtags = []
current_atags = []


def on_card_will_show(text: str, card: Card, kind: str) -> str:
    global current_qtags, current_atags
    js = "<script>"
    js += f"renderPDFLinks({json.dumps(base_path)});"
    question_tags = [getattr(t, "filename", "") for t in current_qtags]
    answer_tags = [getattr(t, "filename", "") for t in current_atags]
    js += f"transformPlayButtonsToAudioElements({json.dumps(question_tags)}, {json.dumps(answer_tags)});"
    if card.autoplay():
        js += "playAudioFiles();"
    js += "</script>"
    current_qtags = []
    current_atags = []
    return text + js


def get_pdf_progress_file() -> Any:
    data = json.loads(consts.PDF_PROGRESS_FILE.read_text(encoding="utf-8"))
    return data


def write_pdf_progress_file(data: Dict) -> None:
    with open(consts.PDF_PROGRESS_FILE, "w") as file:
        json.dump(data, file)


def write_pdf_progress(filename: str, page: int) -> None:
    data = get_pdf_progress_file()
    data[filename] = {"page": page}
    write_pdf_progress_file(data)


def get_pdf_progress(filename: str) -> Dict:
    data = get_pdf_progress_file()
    return data.get(filename, {"page": 1})


def get_audio_progress_file() -> Any:
    data = json.loads(consts.AUDIO_PROGRESS_FILE.read_text(encoding="utf-8"))
    return data


def write_audio_progress_file(data: Dict) -> None:
    with open(consts.AUDIO_PROGRESS_FILE, "w") as file:
        json.dump(data, file)


def write_audio_progress(filename: str, time: float) -> None:
    data = get_audio_progress_file()
    data[filename] = {"time": time}
    write_audio_progress_file(data)


def get_audio_progress(filename: str) -> Dict:
    data = get_audio_progress_file()
    return data.get(filename, {"time": 0})


def handle_js_request(
    handled: Tuple[bool, Any], message: str, context: Any
) -> Tuple[bool, Any]:
    parts = message.split(":")
    cmd = parts[0]
    if cmd != consts.CMD:
        return handled
    ret = None
    subcmd, filename = parts[1:3]
    if filename.endswith(".pdf"):
        if subcmd == "set":
            page = int(parts[3])
            write_pdf_progress(filename, page)
        else:
            ret = get_pdf_progress(filename)
    else:
        if subcmd == "set":
            time = float(parts[3])
            write_audio_progress(filename, time)
        else:
            ret = get_audio_progress(filename)

    return (True, ret)


def write_mpv_conf() -> None:
    "Write a mpv config option to save last position on videos"
    mpv_conf = Path(mw.pm.base) / "mpv.conf"
    mpv_conf.touch(exist_ok=True)
    contents = mpv_conf.read_text(encoding="utf-8")
    if "save-position-on-quit" in contents:
        return
    with open(mpv_conf, "a", encoding="utf-8") as file:
        file.write("save-position-on-quit=yes\n")


def prevent_audio_playback(card: Card, tags: List[AVTag], side: str):
    if not tags:
        # autoplay disabled
        tags = card.question_av_tags() if side == "q" else card.answer_av_tags()
    # prevent Anki from playing audio files and use our mechanism instead
    to_keep = {
        i
        for i, t in enumerate(tags)
        if not isinstance(t, SoundOrVideoTag) or (not is_audio_file(t.filename))
    }
    to_remove = [t for i, t in enumerate(tags) if i not in to_keep]
    if side == "q":
        global current_qtags
        current_qtags = to_remove
    else:
        global current_atags
        current_atags = to_remove
    new_tags = []
    for i in range(len(tags)):
        if i in to_keep:
            new_tags.append(tags[i])
        else:
            # dummy tag to keep sound indices that Anki uses in pycmd valid
            new_tags.append(SoundOrVideoTag(filename=""))
    tags.clear()
    tags.extend(new_tags)


webview_will_set_content.append(append_webcontent)
card_will_show.append(on_card_will_show)
webview_did_receive_js_message.append(handle_js_request)
reviewer_will_play_question_sounds.append(
    lambda c, tags: prevent_audio_playback(c, tags, "q")
)
reviewer_will_play_answer_sounds.append(
    lambda c, tags: prevent_audio_playback(c, tags, "a")
)
write_mpv_conf()
