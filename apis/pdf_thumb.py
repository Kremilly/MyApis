import requests, fitz  # PyMuPDF

from PIL import Image
from io import BytesIO
from http import HTTPStatus
from flask import send_file

class PDFThumb:
    
    @classmethod
    def __init__(cls, params:dict):
        cls.pdf = params['pdf']
        cls.page = params['page']
        cls.width = params['width']
        cls.height = params['height']
    
    @classmethod
    def generate_pdf_thumbnail(cls, url, page_number=0, size=(300, 400)):
        response = requests.get(url)

        if response.status_code == HTTPStatus.OK:
            pdf_document = fitz.open(stream=response.content, filetype='pdf')
            page = pdf_document[page_number]
            
            pix = page.get_pixmap()
            img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            img.thumbnail(size)
            thumbnail_buffer = BytesIO()
            img.save(thumbnail_buffer, format = 'png')
            
            pdf_document.close()
            return thumbnail_buffer
        
        return None
        
    @classmethod
    def get_default_thumbnail(cls):
        response = requests.get('https://i.imgur.com/CvdZqTL.png')

        if response.status_code == HTTPStatus.OK:
            return BytesIO(response.content)
        
        return None
    
    @classmethod
    def get(cls):
        pdf_url = cls.pdf
        page = cls.page if cls.page else 0
        width = cls.width if cls.width else 300
        height = cls.height if cls.height else 400

        if pdf_url:
            thumbnail_buffer = cls.generate_pdf_thumbnail(
                url = pdf_url, 
                page_number = int(page), 
                size = (
                    int(width), int(height)
                )
            )
            
            if thumbnail_buffer:
                thumbnail_buffer.seek(0)
                return send_file(thumbnail_buffer, mimetype = 'image/png')
            
            else:
                default_thumbnail = cls.get_default_thumbnail()
                
                if default_thumbnail:
                    default_thumbnail.seek(0)
                    return send_file(default_thumbnail, mimetype = 'image/png')
                
                return 'Error loading default image', 500
            
        return "Parameter 'pdf' missing", 400
