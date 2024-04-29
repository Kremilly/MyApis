#!/usr/bin/python3

import qrcode

from io import BytesIO
from flask import Response, jsonify

class QRCode:
    
    @classmethod
    def __init__(cls, params):
        cls.url = params['url']
    
    @classmethod
    def get(cls) -> BytesIO:
        if cls.url is None:
            return jsonify({"error": "Parameter 'url' not provided"}), 400
        
        qr = qrcode.QRCode(
            border=4,
            version=1,
            box_size=10,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
        )
        
        qr.add_data(cls.url)
        qr.make(fit=True)

        qr_image = qr.make_image(
            fill_color='black', 
            back_color='white',
        )

        img_byte_array = BytesIO()
        qr_image.save(img_byte_array, format='PNG')

        img_byte_array.seek(0)
        
        return Response(
            img_byte_array.getvalue(), 
            content_type='image/png'
        )
