"""
Install LibreOffice if it isn't found, then convert everything in input_files/ to PDF.

    python install_and_convert.py            # asks before installing
    python install_and_convert.py --yes      # installs without asking
    python install_and_convert.py --dry-run  # only shows what it would run
"""
import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time

from convert_to_pdf import convert_any_to_pdf, locate_soffice

DOWNLOAD_URL = "https://www.libreoffice.org/download/"


def _can_print(chars):
    try:
        chars.encode(sys.stdout.encoding or "ascii")
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def run_with_spinner(cmd, label="Installing LibreOffice"):
    """
    Run cmd while showing a live status line: spinner, bouncing bar, elapsed time
    and the installer's latest message. Returns (exit_code, output_lines).
    """
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏" if _can_print("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏") else "|/-\\"
    lines, last = [], [""]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")

    def reader():
        for raw in proc.stdout:
            # installers redraw progress with \r; keep the newest readable piece
            for part in raw.split("\r"):
                text = re.sub(r"[^\x20-\x7e]+", " ", part).strip()
                if len(text) > 2 and text.strip("-\\|/ ") != "":
                    lines.append(text)
                    last[0] = text

    threading.Thread(target=reader, daemon=True).start()

    animate = sys.stdout.isatty()
    start, i, width, prev_minute = time.time(), 0, 10, -1
    while proc.poll() is None:
        elapsed = int(time.time() - start)
        if animate:
            pos = i % (2 * (width - 4))
            pos = pos if pos <= width - 4 else 2 * (width - 4) - pos
            bar = " " * pos + "====" + " " * (width - 4 - pos)
            cols = shutil.get_terminal_size((80, 20)).columns
            line = f"{frames[i % len(frames)]} {label} [{bar}] {elapsed // 60}:{elapsed % 60:02d}  {last[0]}"
            sys.stdout.write("\r" + line[: cols - 1].ljust(cols - 1))
            sys.stdout.flush()
        elif elapsed // 60 != prev_minute:  # not a terminal: one line per minute
            prev_minute = elapsed // 60
            print(f"{label}... {elapsed // 60} min elapsed", flush=True)
        i += 1
        time.sleep(0.1)

    proc.wait()
    elapsed = int(time.time() - start)
    if animate:
        cols = shutil.get_terminal_size((80, 20)).columns
        sys.stdout.write("\r" + " " * (cols - 1) + "\r")
    took = f"{elapsed // 60}:{elapsed % 60:02d}"
    if proc.returncode == 0:
        print(f"{'✔' if _can_print('✔') else 'OK'} Install finished in {took}")
    else:
        print(f"{'✘' if _can_print('✘') else 'X'} Install failed after {took}")
    return proc.returncode, lines


def install_command():
    """Return the package-manager command that installs LibreOffice on this OS, or None."""
    system = platform.system()

    if system == "Windows":
        if shutil.which("winget"):
            return ["winget", "install", "--id", "TheDocumentFoundation.LibreOffice", "--exact",
                    "--silent", "--accept-package-agreements", "--accept-source-agreements"]
        if shutil.which("choco"):
            return ["choco", "install", "libreoffice-fresh", "-y"]
        return None

    if system == "Darwin":
        if shutil.which("brew"):
            return ["brew", "install", "--cask", "libreoffice"]
        return None

    # Linux: use whichever package manager is present, with sudo when not root
    sudo = [] if os.geteuid() == 0 else ["sudo"]
    managers = [
        ("apt-get", ["apt-get", "install", "-y", "libreoffice"]),
        ("dnf", ["dnf", "install", "-y", "libreoffice"]),
        ("pacman", ["pacman", "-S", "--noconfirm", "libreoffice-fresh"]),
        ("zypper", ["zypper", "--non-interactive", "install", "libreoffice"]),
    ]
    for tool, cmd in managers:
        if shutil.which(tool):
            if tool == "apt-get":
                # refresh package lists first so the install doesn't 404
                return ["sh", "-c", " ".join(sudo + ["apt-get", "update"]) + " && " + " ".join(sudo + cmd)]
            return sudo + cmd
    return None


def main():
    parser = argparse.ArgumentParser(description="Install LibreOffice if needed, then convert files to PDF.")
    parser.add_argument("-y", "--yes", action="store_true", help="install without asking")
    parser.add_argument("--dry-run", action="store_true", help="show the install command without running it")
    args = parser.parse_args()

    soffice = locate_soffice()
    if soffice:
        print(f"LibreOffice found: {soffice}")
        convert_any_to_pdf(soffice)
        return

    print("LibreOffice is not installed.")
    cmd = install_command()
    if not cmd:
        sys.exit(f"No supported package manager found. Install LibreOffice from {DOWNLOAD_URL} and run again.")

    print("Install command:\n  " + " ".join(cmd))
    if args.dry_run:
        return
    if not args.yes:
        try:
            answer = input("Install LibreOffice now? This can take several minutes. [y/N] ")
        except EOFError:
            answer = ""
        if answer.strip().lower() not in ("y", "yes"):
            sys.exit("Cancelled. Nothing was installed.")

    # ask for the sudo password now, before the spinner hides the prompt
    if "sudo" in cmd or (cmd[0] == "sh" and "sudo" in cmd[-1]):
        if subprocess.run(["sudo", "-v"]).returncode != 0:
            sys.exit("Could not get sudo permission. Nothing was installed.")

    print("This can take several minutes (LibreOffice is about 350 MB).\n")
    code, output = run_with_spinner(cmd)  # blocks until the installer finishes
    if code != 0:
        if output:
            print("\nLast installer output:")
            for line in output[-15:]:
                print("  " + line)
        sys.exit(f"\nInstallation failed (exit code {code}). "
                 f"Install it manually from {DOWNLOAD_URL} and run again.")

    soffice = locate_soffice()
    if not soffice:
        sys.exit("\nInstallation finished, but LibreOffice still wasn't found. "
                 "Open a new terminal and run `python convert_to_pdf.py`, "
                 "or set SOFFICE_PATH to the full path of soffice.")

    print(f"LibreOffice installed: {soffice}\n")
    convert_any_to_pdf(soffice)


if __name__ == "__main__":
    main()
