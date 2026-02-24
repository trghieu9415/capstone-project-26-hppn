import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from autocorrect import Speller

def ocr_pdf_with_pymupdf(pdf_path, output_txt_path):
    print(f"Đang xử lý OCR file: {pdf_path} bằng PyMuPDF...")
    
    try:
        # Mở file PDF
        doc = fitz.open(pdf_path)
        extracted_text = []
        total_pages = len(doc)
		
        spell = Speller(lang='vi')        
        for page_num in range(total_pages):
            print(f"Đang đọc chữ trang {page_num + 1}/{total_pages}...")
            
            # Lấy trang hiện tại
            page = doc.load_page(page_num)
            
            # Tăng độ phân giải ảnh (zoom) để Tesseract nhận diện chữ chính xác hơn
            # Mức zoom = 2 tương đương khoảng 144 - 150 DPI
            zoom_matrix = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=zoom_matrix)
            
            # Chuyển đổi dữ liệu ảnh (pixmap) sang định dạng PIL Image
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            
            # Chạy Tesseract OCR (ngôn ngữ Tiếng Việt)
            text = pytesseract.image_to_string(img, lang='vie')
            text = spell(text)
            extracted_text.append(text)
            
        # Ghi toàn bộ text ra file
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write("\n\n--- Trang tiếp theo ---\n\n".join(extracted_text))
            
        print(f"✅ Hoàn tất! Đã trích xuất text và lưu tại: {output_txt_path}")

    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    input_pdf = "DCT.pdf" 
    output_text_file = "DCTTEXT.txt"
    
    if os.path.exists(input_pdf):
        ocr_pdf_with_pymupdf(input_pdf, output_text_file)
    else:
        print(f"Không tìm thấy file {input_pdf}.")