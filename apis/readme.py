import requests

from flask import jsonify
from http import HTTPStatus

class ReadmeDevToPosts:

    @classmethod    
    def __init__(cls, params:dict):
        cls.username = params['username']
        
        cls.color = '#' + params['color'].replace(
            '#', ''
        ) if params['color'] else '#58a6ff'

    @classmethod
    def generate_svg(cls, articles):
        svg_height = len(articles) * 40
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="500" height="{svg_height}">'
        
        for i, article in enumerate(articles):
            y_position = (i + 1) * 35
            
            svg += f'<a href="{article["url"]}" target="_blank">'
            svg += f'<text x="15" y="{y_position}" font-size="14" fill="{cls.color}" style="text-decoration: none; font-weight: bold;" font-family="Segoe UI,Ubuntu,Helvetica Neue,Sans-Serif">{article["title"]}</text>'
            svg += '</a>'
        svg += '</svg>'
        
        return svg

    @classmethod
    def get(cls):
        devto_api_url = f'https://dev.to/api/articles?username={cls.username}'
        
        try:
            response = requests.get(devto_api_url)
            
            if response.status_code == HTTPStatus.OK:
                articles = [{
                    'title': article['title'], 'url': article['url']
                } for article in response.json()]
                
                return cls.generate_svg(articles), HTTPStatus.OK, {
                    'Content-Type': 'image/svg+xml'
                }
            else:
                return jsonify({
                    'error': 'Failed to fetch posts from Dev.to.'
                }), response.status_code
            
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), HTTPStatus.INTERNAL_SERVER_ERROR
