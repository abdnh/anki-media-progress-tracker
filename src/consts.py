from pathlib import Path

NAME = "Media Viewing Progress Tracker"
CMD = "media-progress-tracker"
ADDON_DIR = Path(__file__).parent
USER_FILES = ADDON_DIR / Path("user_files")
USER_FILES.mkdir(exist_ok=True)
PDF_PROGRESS_FILE = USER_FILES / "pdf.json"
if not PDF_PROGRESS_FILE.exists():
    PDF_PROGRESS_FILE.write_text("{}", encoding="utf-8")
