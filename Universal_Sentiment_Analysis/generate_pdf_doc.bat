@echo off
echo Installing PDF Generator...
.venv\Scripts\python -m pip install fpdf

echo Generating PDF...
.venv\Scripts\python make_pdf_doc.py

if exist Project_Explanation.pdf (
    echo PDF Created Successfully!
    start Project_Explanation.pdf
) else (
    echo PDF Creation Failed.
)
pause
