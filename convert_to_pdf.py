import os
import platform
import shutil
import subprocess
import sys

INPUT_FOLDER = "input_files"
OUTPUT_FOLDER = "output_pdf"

SUPPORTED_EXTS = (
    ".doc", ".docx", ".odt", ".rtf", ".txt", ".html", ".xml",
    ".xls", ".xlsx", ".ods", ".csv",
    ".ppt", ".pptx", ".odp",
    ".odg", ".svg",
)


def locate_soffice():
    """
    Return the path of the LibreOffice executable, or None if it isn't installed.
    Order: SOFFICE_PATH env var -> PATH -> default install locations.
    """
    env_path = os.environ.get("SOFFICE_PATH")
    if env_path:
        if os.path.isfile(env_path):
            return env_path
        sys.exit(f"SOFFICE_PATH is set but not found: {env_path}")

    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found

    system = platform.system()
    if system == "Windows":
        candidates = [
            os.path.join(os.environ.get(var, ""), "LibreOffice", "program", "soffice.exe")
            for var in ("ProgramFiles", "ProgramFiles(x86)")
            if os.environ.get(var)
        ]
    elif system == "Darwin":
        candidates = ["/Applications/LibreOffice.app/Contents/MacOS/soffice"]
    else:
        candidates = ["/usr/bin/soffice", "/usr/lib/libreoffice/program/soffice", "/snap/bin/libreoffice"]

    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def find_soffice():
    """Like locate_soffice(), but exit with a helpful message if it's missing."""
    path = locate_soffice()
    if path:
        return path
    sys.exit(
        "LibreOffice not found. Run `python install_and_convert.py` to install it, "
        "install it from https://www.libreoffice.org/download/, "
        "or set SOFFICE_PATH to the full path of soffice."
    )


def convert_any_to_pdf(office_cmd=None):
    """Convert every supported file in INPUT_FOLDER to PDF in OUTPUT_FOLDER."""
    if not os.path.isdir(INPUT_FOLDER):
        sys.exit(f"Input folder not found: {INPUT_FOLDER}")

    office_cmd = office_cmd or find_soffice()
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    files = sorted(f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(SUPPORTED_EXTS))
    if not files:
        print(f"No supported files in {INPUT_FOLDER}/")
        return

    failed = []
    for file in files:
        input_path = os.path.join(INPUT_FOLDER, file)
        print(f"Converting: {input_path}")
        result = subprocess.run(
            [office_cmd, "--headless", "--convert-to", "pdf", "--outdir", OUTPUT_FOLDER, input_path],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            failed.append(file)
            print(f"  failed: {result.stderr.strip() or result.stdout.strip()}")

    done = len(files) - len(failed)
    print(f"\nConverted {done}/{len(files)} files. PDFs saved in: {OUTPUT_FOLDER}")
    if failed:
        print("Failed:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    convert_any_to_pdf()
