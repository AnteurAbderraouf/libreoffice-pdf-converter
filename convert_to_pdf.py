import os
import subprocess
import platform

INPUT_FOLDER = "input_files" 
OUTPUT_FOLDER = "output_pdf"

def convert_any_to_pdf():
    """
    Convert all LibreOffice-supported files in INPUT_FOLDER to PDF in OUTPUT_FOLDER.
    Includes: .doc, .docx, .odt, .ppt, .pptx, .xls, .xlsx, .odp, .ods, etc.
    """

    # Detect the correct LibreOffice executable
    if platform.system() == "Windows":
        office_cmd = r"C:\Program Files\LibreOffice\program\soffice.exe" # Put your full path to libre soffice.exe
    else:
        office_cmd = "libreoffice"


    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


    supported_exts = (
        ".doc", ".docx", ".odt",
        ".ppt", ".pptx", ".odp",
        ".xls", ".xlsx", ".ods",
        ".rtf", ".txt", ".csv", ".html", ".xml" 
    )


    for file in os.listdir(INPUT_FOLDER):
        if file.lower().endswith(supported_exts):
            input_path = os.path.join(INPUT_FOLDER, file)
            print(f"Converting: {input_path}")

            subprocess.run([
                office_cmd,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", OUTPUT_FOLDER,
                input_path
            ], check=True)

    print("\n✅ All supported files converted. PDFs saved in:", OUTPUT_FOLDER)

if __name__ == "__main__":
    convert_any_to_pdf()
