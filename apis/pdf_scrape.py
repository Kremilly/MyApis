import urllib.request, os, requests, tempfile 

from flask import jsonify
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup

class PDFScrape:
    
    def __init__(cls, params:dict):
        cls.url = params['url']
    
    def format_filesize(cls, size, units=[ 'bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB' ]):
        return str(size) + ' ' + units[0] if size < 1024 else cls.format_filesize(
            size >> 10, units[1:]
        )
    
    def get_pdf_filename(cls):
        return os.path.basename(cls.url)
    
    def check_pdf_password(cls):
        with urllib.request.urlopen(cls.url) as response:
            pdf_data = response.read()

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(pdf_data)
            tmp_file_name = tmp_file.name

        with open(tmp_file_name, 'rb') as pdf_file:
            if PdfReader(pdf_file).is_encrypted:
                return True
            
            return False
        
    def get_total_pages(cls):
        with urllib.request.urlopen(cls.url) as response:
            pdf_data = response.read()

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(pdf_data)
            tmp_file_name = tmp_file.name

        with open(tmp_file_name, 'rb') as pdf_file:
            return len(PdfReader(pdf_file).pages)
    
    def get_pdf_filesize(cls):
        pdf_response = requests.get(cls.url)
        pdf_response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(pdf_response.content)
            tmp_file_name = tmp_file.name
        
        with open(tmp_file_name, 'rb') as pdf_file:
            file_size = os.path.getsize(tmp_file_name)
            return cls.format_filesize(file_size)
    
    def get_pdf_status_code(cls):
        response = requests.get(cls.url)
        return response.status_code
    
    def get(cls):
        try:
            books_list = []
            
            response = requests.get(cls.url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                if href.endswith('.pdf'):
                    pdf_url = href
                    
                    if pdf_url is not None and pdf_url not in books_list:
                        books_list.append({
                            'url': pdf_url,
                            'name': cls.get_pdf_filename(),
                            'pages': cls.get_total_pages(),
                            'size': cls.get_pdf_filesize(),
                            'encrypted': cls.check_pdf_password(),
                            'status_code': cls.get_pdf_status_code(),
                        })
                    
            return jsonify({
                'list': books_list,
                'total': len(books_list)
            }), 200, {
                'Content-Type': 'application/json'
            }
                
        except requests.exceptions.HTTPError as err:
            return jsonify({
                'success': False,
                'status': err.response.status_code,
                'message': f'Error accessing the page: {cls.url}',
            }), err.response.status_code, {
                'Content-Type': 'application/json'
            }
            
        except requests.exceptions.ConnectionError as err:
            return jsonify({
                'success': False,
                'message': f'Connection error with the url: {cls.url}',
            }), 500, {
                'Content-Type': 'application/json'
            }
