#!/opt/anaconda3/envs/watermark/bin/python3

"""Script to add a watermark to PDF files.

This script allows you to add a watermark to PDF files, either at the front or back of the existing content.
"""
import argparse
import logging
import tempfile
import uuid
from pathlib import Path

from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

MAX_TEXT_LENGTH = 28  # including spaces

def create_watermark(text, output_file_path=None):
    """Creates a PDF watermark with the given text.

    Args:
        text (str): Text to be used in the watermark. Must be less than 28 characters.
        output_file_path (str, optional): Output file path for the watermark PDF. 
            If not provided, a temporary file will be created.

    Returns:
        str: Path to the created watermark PDF file.
    """
    assert len(text) < MAX_TEXT_LENGTH
    
    if output_file_path is None:
        unique_id = uuid.uuid4().hex[:8]
        _, output_file_path = tempfile.mkstemp(
            suffix=f"_{unique_id}.pdf", prefix="watermark_" + text, dir=tempfile.gettempdir())
    output_file_path = correct_pdf_path(Path(output_file_path))

    pdf = canvas.Canvas(str(output_file_path), pagesize=A4)
    pdf.setFillColor(colors.gray, alpha=0.6)
    pdf.setFont("Helvetica", 50)
    pdf.rotate(45)
    pdf.drawCentredString(500, 100, text)
    pdf.save()
    return output_file_path

def correct_pdf_path(file_path):
    return file_path if file_path.suffix == ".pdf" else file_path.with_suffix(".pdf")

def duplicate_watermark(watermark_path, page_count, output_file_path=None):
    """Duplicates the watermark to match the specified number of pages.

    Args:
        watermark_path (str): Path to the original watermark PDF file.
        page_count (int): Number of pages to duplicate the watermark.
        tmp_file_path (str, optional): Output file path for the duplicated watermark. 
            If not provided, a temporary file will be created.

    Returns:
        str: Path to the temporary file containing the duplicated watermark PDF.
    """
    if output_file_path is None:
        unique_id = uuid.uuid4().hex[:8]
        _, output_file_path = tempfile.mkstemp(
            suffix=f"_{unique_id}.pdf", prefix="watermark_tmp", dir=tempfile.gettempdir())
    output_file_path = correct_pdf_path(Path(output_file_path))

    tmp_output = PdfFileWriter()
    with open(watermark_path, "rb") as watermark_file:
        watermark_pdf = PdfFileReader(watermark_file)
        watermark_page = watermark_pdf.getPage(0)
        for _ in range(page_count):
            tmp_output.addPage(watermark_page)
        with open(output_file_path, "wb") as tmp_output_file:
            tmp_output.write(tmp_output_file)
    return output_file_path

def ensure_new_file(file_path):
    """Ensures a new file path by appending an index to the original file name if it already exists.

    Args:
        file_path (Path): The original file path.

    Returns:
        Path: The new file path with an appended index.
    """
    index = 1
    while file_path.exists():
        file_path = Path(file_path.parent, f"{file_path.stem}_{index}{file_path.suffix}")
        index += 1
    return file_path

def add_watermark(input_file_path, watermark_file_path):
    """Adds watermark to the specified position in the input PDF file.

    Args:
        input_file_path (str): Path to the input PDF file.
        watermark_file_path (str): Path to the watermark PDF file.
        position (str, optional): Position of the watermark relative to the text, 
            either "back" or "front". Defaults to "back".
    """
    input_file_path = Path(input_file_path)
    new_file_path = Path(input_file_path.parent, f"{input_file_path.stem}_watermarked.pdf")
    new_file_path = ensure_new_file(new_file_path)

    with open(input_file_path, "rb") as input_file:
        input_pdf = PdfFileReader(input_file)
        page_count = input_pdf.getNumPages()
        tmp_watermark_file_path = duplicate_watermark(watermark_file_path, page_count)
        output = PdfFileWriter()
        with open(tmp_watermark_file_path, "rb") as tmp_watermark_file:
            tmp_watermark_pdf = PdfFileReader(tmp_watermark_file)
            for i in range(page_count):
                pdf_page = input_pdf.getPage(i)
                pdf_page.merge_page(tmp_watermark_pdf.getPage(i))
                output.addPage(pdf_page)

            with open(new_file_path, "wb") as new_file:
                output.write(new_file)

def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    """Main entry point for the script.
    Parses command-line arguments and adds watermarks to specified PDF files.
    """
    parser = argparse.ArgumentParser(description="Add watermark to a PDF file.")
    parser.add_argument("watermark_text", help="Text for the watermark.")
    parser.add_argument(
        "-f",
        "--input_files",
        help="Path to the input PDF files.",
        nargs="*", 
        required=False,
        default=None,
        metavar="file_name")
    parser.add_argument(
        "-x",
        "--exclude",
        help="File names to exclude.",
        nargs="*",
        required=False,
        default=None,
        metavar="file_name")

    args = parser.parse_args()
    exclude_list = [] if args.exclude is None else args.exclude
    file_list = [] if args.input_files is None else args.input_files
    cwd = Path.cwd()
    if not file_list:
        file_list = [f for f in cwd.glob("*.pdf") if f.name not in exclude_list]
    else:
        file_list = [f for f in args.input_files if Path(f).name not in exclude_list]
    watermark_file_path = create_watermark(args.watermark_text)
    
    setup_logging()
    for input_file in file_list:
        logging.info("Processing file: %s", input_file)
        add_watermark(
            input_file, watermark_file_path)
    logging.info("All done!")

if __name__ == "__main__":
    main()
