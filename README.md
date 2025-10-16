# LibreOffice PDF Converter

A Python script that converts any LibreOffice-supported document (Word, PowerPoint, Excel, etc.) into PDF automatically using LibreOffice in headless mode.

## Features
- Supports "doc","docx","odt","rtf","txt","html","xml","xls","xlsx","ods","csv","ppt","pptx","odp","odg","svg"
- Bulk converts all files inside `input_files` to PDFs in `output_pdf`.

## Requirements
- Python 3.x  
- LibreOffice installed and available in PATH  

## How to Use
1. Place your files in the `input_files` folder.  
2. Run the script:
   ```bash
   python convert_to_pdf.py
