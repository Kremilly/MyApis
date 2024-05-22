import requests

from flask import Response
from http import HTTPStatus
from bs4 import BeautifulSoup

class SciHub:
    
    DEFAULT_DOMAIN = 'https://sci-hub.se/'
    
    @classmethod
    def __init__(cls, params:dict):
        cls.paper = cls.get_paper_doi(params['paper'])
        
    @classmethod
    def get_paper_doi(cls, paper):
        if 'http://' in paper or 'https://' in paper:
            return paper.split("/", 3)[-1]
                
        return paper
        
    @classmethod
    def get(cls):
        response = requests.get(f'{cls.DEFAULT_DOMAIN}{cls.paper}')
        
        if response.status_code == HTTPStatus.OK:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            embed_tag = soup.find('embed')
            src_value = embed_tag.get('src').split('#')[0] # type: ignore
            
            if src_value.startswith('//'):
                src_value = 'https:' + src_value
            
            response = requests.get(src_value)
            if response.status_code == HTTPStatus.OK:
                return Response(
                    response.content, content_type='application/pdf'
                )
