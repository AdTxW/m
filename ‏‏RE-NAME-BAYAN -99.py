import os
import pdfplumber
import re
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# تحميل بيانات الاعتماد من Google Drive
def download_credentials_from_drive(file_id, destination):
    credentials_service = build('drive', 'v3', credentials=service_account.Credentials.from_service_account_file('path/to/your/local/service/account/credentials.json'))
    request = credentials_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

# تحديد معرف ملف بيانات الاعتماد في Google Drive
credentials_file_id = '1aFlpYaHfXby7iDJhykB0u1MilniXPPSL'
local_credentials_path = '/workspaces/m/husssein-9905204ce60a.json'

# تنزيل ملف بيانات الاعتماد إلى المسار المحلي
download_credentials_from_drive(credentials_file_id, local_credentials_path)

# تحميل بيانات الاعتماد
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
        local_credentials_path, scopes=SCOPES)

# إعداد خدمة Google Drive API
service = build('drive', 'v3', credentials=credentials)

def download_file(file_id, destination):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

def find_files_by_pattern_from_drive(folder_id, pattern):
    """البحث عن جميع الملفات في المجلد بناءً على نمط معين من Google Drive."""
    query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'"
    results = service.files().list(q=query).execute()
    files = []
    for item in results.get('files', []):
        if re.match(pattern, item['name']):
            files.append(item)
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

def rename_files_with_invoice_numbers_from_drive(folder_id, pattern, download_directory):
    files = find_files_by_pattern_from_drive(folder_id, pattern)
    if not files:
        print("لم يتم العثور على أي ملفات مناسبة في المجلد.")
        return

    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    for file in files:
        file_id = file['id']
        file_name = file['name']
        destination = os.path.join(download_directory, file_name)
        download_file(file_id, destination)
        invoice_number = extract_invoice_number(destination)
        if invoice_number:
            new_file_name = f"{invoice_number}.pdf"
            new_file_path = os.path.join(download_directory, new_file_name)
            os.rename(destination, new_file_path)
            print(f"تمت إعادة تسمية الملف {file_name} إلى: {new_file_name}")
        else:
            print(f"لم يتم العثور على رقم البيان في الملف: {file_name}")

# تحديد معرف المجلد في Google Drive ونمط اسم الملف
folder_id = '17SFDGNhBWDtVQENMSThg6IfFGJcdQoxq'
file_pattern = r"\d{8}_\d{7}\.pdf"  # نمط الملف: تاريخ وأرقام مكونة من 8 و 7 أرقام
download_directory = '/workspaces/m/Downloads'  # مسار الدليل لتنزيل الملفات في بيئة العمل الخاصة بك

# إعادة تسمية الملفات بناءً على رقم البيان
rename_files_with_invoice_numbers_from_drive(folder_id, file_pattern, download_directory)
