from typing import Any, Dict
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
)

from . import consts

base_path = f"/_addons/{mw.addonManager.addonFromModule(__name__)}/web"
mw.addonManager.setWebExports(__name__, r"web/.*")


def append_webcontent(webcontent: WebContent, context: Any) -> None:

    if isinstance(context, (Reviewer, Previewer, CardLayout)):
        webcontent.js.append(f"{base_path}/pdf.js")
        webcontent.css.append(f"{base_path}/pdf.css")


def render_pdf_links(text: str, card: Card, kind: str) -> str:
    return text + f"<script>renderPDFLinks({json.dumps(base_path)})</script>"


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


def handle_js_request(
    handled: tuple[bool, Any], message: str, context: Any
) -> tuple[bool, Any]:
    parts = message.split(":")
    cmd = parts[0]
    if cmd != consts.CMD:
        return handled
    ret = None
    subcmd, filename = parts[1:3]
    if subcmd == "set":
        page = int(parts[3])
        write_pdf_progress(filename, page)
    else:
        ret = get_pdf_progress(filename)
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


webview_will_set_content.append(append_webcontent)
card_will_show.append(render_pdf_links)
webview_did_receive_js_message.append(handle_js_request)
write_mpv_conf()
