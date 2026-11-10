# LibreOffice PDF Converter

Bulk-convert Word, Excel, PowerPoint, OpenDocument and other office files to PDF with one Python script, using LibreOffice in headless mode. Drop files in a folder, run it, get PDFs.

## Features

- **Many formats:** `doc` `docx` `odt` `rtf` `txt` `html` `xml` · `xls` `xlsx` `ods` `csv` · `ppt` `pptx` `odp` · `odg` `svg`
- **Finds LibreOffice by itself** on Windows, macOS and Linux (checks `PATH` and the default install folders).
- **Batch mode:** converts everything in `input_files/` into `output_pdf/`.
- **Keeps going on errors:** a file that fails is reported at the end instead of stopping the run.
- **No dependencies** beyond the Python standard library.

## Requirements

- Python 3.8+
- [LibreOffice](https://www.libreoffice.org/download/)

## Usage

1. Put your files in the `input_files/` folder.
2. Run the script:

   ```bash
   python convert_to_pdf.py
   ```

3. Your PDFs appear in `output_pdf/`.

### LibreOffice in a custom location

If LibreOffice is installed somewhere the script doesn't check, point to it with `SOFFICE_PATH`:

```bash
# macOS / Linux
SOFFICE_PATH=/opt/libreoffice/program/soffice python convert_to_pdf.py
```

```powershell
# Windows (PowerShell)
$env:SOFFICE_PATH = "D:\Apps\LibreOffice\program\soffice.exe"; python convert_to_pdf.py
```

## Samples

`input_files/` has one sample of each supported format, and `output_pdf/` shows the converted results.

## Notes

- Close LibreOffice before running. An open LibreOffice window can make headless conversion fail silently.
- A PDF with the same name in `output_pdf/` gets overwritten.
