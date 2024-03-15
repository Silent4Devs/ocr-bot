import os
import pytesseract
from pdf2image import convert_from_path
from tqdm import tqdm   
import pdfplumber

# Function to extract images from PDF
def extract_images_from_pdf(pdf_bytes):
    images = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            for image in page.images:
                images.append(image.to_image())
    return images

# Function to convert images to text using OCR
def image_to_text(image):
    text = pytesseract.image_to_string(image, lang='spa', config='--oem 1 --psm 3')
    return text

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    pages = convert_from_path(pdf_path)
    text = ""
    for page_num, page in enumerate(tqdm(pages, desc="Extracting text", unit="page")):
        text += f"Page {page_num + 1}:\n"
        text += image_to_text(page)
        text += "\n\n"
    return text

def write_ocr_text_to_file(text, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"OCR text saved to {output_file}")
    except Exception as e:
        print(f"Failed to save OCR text to {output_file}: {e}")

# Main function
def main():
    file_name = "BASES009"
    pdf_path = "pdf/" + file_name + ".pdf"
    output_file = file_name + ".txt"
    output_file_full_path = os.path.join(os.path.dirname("txt/"), output_file)
    if not os.path.isfile(pdf_path):
        print("Invalid PDF file path.")
        return
    text = pdf_to_text(pdf_path)
    write_ocr_text_to_file(text, output_file_full_path)
    print("Text extracted from PDF:\n", text)

if __name__ == "__main__":
    main()


