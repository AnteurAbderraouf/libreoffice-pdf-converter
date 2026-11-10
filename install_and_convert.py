"""
Install LibreOffice if it isn't found, then convert everything in input_files/ to PDF.

    python install_and_convert.py            # asks before installing
    python install_and_convert.py --yes      # installs without asking
    python install_and_convert.py --dry-run  # only shows what it would run
"""
import argparse
import os
import platform
import shutil
import subprocess
import sys

from convert_to_pdf import convert_any_to_pdf, locate_soffice

DOWNLOAD_URL = "https://www.libreoffice.org/download/"


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

    print("\nInstalling LibreOffice, please wait...\n")
    result = subprocess.run(cmd)  # blocks until the installer finishes
    if result.returncode != 0:
        sys.exit(f"\nInstallation failed (exit code {result.returncode}). "
                 f"Install it manually from {DOWNLOAD_URL} and run again.")

    soffice = locate_soffice()
    if not soffice:
        sys.exit("\nInstallation finished, but LibreOffice still wasn't found. "
                 "Open a new terminal and run `python convert_to_pdf.py`, "
                 "or set SOFFICE_PATH to the full path of soffice.")

    print(f"\nLibreOffice installed: {soffice}\n")
    convert_any_to_pdf(soffice)


if __name__ == "__main__":
    main()
