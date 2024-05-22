from asyncio.windows_events import NULL
import io, urllib.request, os, requests, tempfile 

from flask import jsonify
from PyPDF2 import PdfReader, PdfFileReader

class PDFInfo:
    
    def __init__(cls, params:dict):
        cls.pdf = params['pdf']
    
    def format_filesize(cls, size, units=[ 'bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB' ]):
        return str(size) + ' ' + units[0] if size < 1024 else cls.format_filesize(
            size >> 10, units[1:]
        )
    
    def get_pdf_filename(cls):
        return os.path.basename(cls.pdf)
    
    def check_pdf_password(cls):
        response = requests.get(cls.pdf)
        response.raise_for_status()
        pdf_bytes = response.content
        
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PdfReader(pdf_file)
        
        return pdf_reader.is_encrypted
        
    def get_total_pages(cls):
        total_pages = NULL
        
        if not cls.check_pdf_password():
            response = requests.get(cls.pdf)
            response.raise_for_status()
            pdf_bytes = response.content
            
            pdf_file = io.BytesIO(pdf_bytes)
            
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
        
        return total_pages
    
    def get_pdf_filesize(cls):
        pdf_response = requests.get(cls.pdf)
        pdf_response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(pdf_response.content)
            tmp_file_name = tmp_file.name
        
        with open(tmp_file_name, 'rb') as pdf_file:
            file_size = os.path.getsize(tmp_file_name)
            return cls.format_filesize(file_size)
    
    def get_pdf_status_code(cls):
        response = requests.get(cls.pdf)
        return response.status_code
    
    def get(cls):
        try:
            return jsonify({
                'url': cls.pdf,
                'name': cls.get_pdf_filename(),
                'pages': cls.get_total_pages(),
                'size': cls.get_pdf_filesize(),
                'encrypted': cls.check_pdf_password(),
                'status_code': cls.get_pdf_status_code(),
            }), 200, {
                'Content-Type': 'application/json'
            }
        except requests.exceptions.HTTPError as err:
            return jsonify({
                'success': False,
                'status': err.response.status_code,
                'message': f'Error accessing the page: {cls.pdf}',
            }), err.response.status_code, {
                'Content-Type': 'application/json'
            }
            
        except requests.exceptions.ConnectionError as err:
            return jsonify({
                'success': False,
                'message': f'Connection error with the url: {cls.pdf}',
            }), 500, {
                'Content-Type': 'application/json'
            }
