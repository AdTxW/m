import os
import pdfplumber
import re

def find_files_by_pattern(directory, pattern):
    """البحث عن جميع الملفات في الدليل بناءً على نمط معين."""
    files = []
    for filename in os.listdir(directory):
        if re.match(pattern, filename):
            files.append(os.path.join(directory, filename))
    return files

def extract_invoice_number(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"الملف غير موجود في المسار: {pdf_path}")
        return None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                first_table = tables[0]  # استخدام أول جدول موجود
                if first_table:
                    # التحقق من وجود أكثر من سطر في الجدول
                    if len(first_table) > 1 and len(first_table[0]) > 0:
                        # الحصول على محتوى الخلية أسفل الترويسة
                        invoice_number = first_table[1][0].strip()
                        print(f"محتوى الخلية أسفل الترويسة: {invoice_number}")
                        return invoice_number
    
    return None

def rename_files_with_invoice_numbers(directory, pattern):
    files = find_files_by_pattern(directory, pattern)
    if not files:
        print("لم يتم العثور على أي ملفات مناسبة في المجلد.")
        return

    for pdf_path in files:
        invoice_number = extract_invoice_number(pdf_path)
        if invoice_number:
            new_file_name = f"{invoice_number}.pdf"
            new_file_path = os.path.join(directory, new_file_name)
            os.rename(pdf_path, new_file_path)
            print(f"تمت إعادة تسمية الملف {os.path.basename(pdf_path)} إلى: {new_file_name}")
        else:
            print(f"لم يتم العثور على رقم البيان في الملف: {os.path.basename(pdf_path)}")

# تحديد الدليل ونمط اسم الملف
directory_path = r"C:\Users\admin1\Downloads"
file_pattern = r"\d{8}_\d{7}\.pdf"  # نمط الملف: تاريخ وأرقام مكونة من 8 و 7 أرقام

# إعادة تسمية الملفات بناءً على رقم البيان
rename_files_with_invoice_numbers(directory_path, file_pattern)
