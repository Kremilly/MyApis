import json, requests

from http import HTTPStatus

class Wikipedia:
    
    @classmethod
    def __init__(cls, params:dict):
        cls.search = params['term']
        cls.location = params['location']
        cls.thumb_size = params['thumb_size']
        cls.short_summary = params['short_summary']
        
    @classmethod
    def validate_location(cls):
        with open('./data/wikipedia_locations.json', 'rb') as content:
            locations = content.read().decode('utf-8')
        
        locations_json = json.loads(locations)
        
        for l in locations_json:
            if cls.location == l:
                return 'location_valid'
            
        return 'location_invalid'
    
    @classmethod
    def api_url(cls) -> str:
        return f'https://{cls.location}.wikipedia.org/w/api.php'
    
    @classmethod
    def get_thumbnail(cls) -> dict:
        image_size = cls.thumb_size or 500
        
        response = requests.get(cls.api_url(), params={
            'format': 'json',
            'action': 'query',
            'titles': cls.search,
            'formatversion': 2,
            'prop': 'pageimages',
            'pithumbsize': image_size,
        })

        if response.status_code == HTTPStatus.OK:
            data = response.json()
            pages = data.get('query', {}).get('pages', [])
            
            if pages:
                for page in pages:
                    if 'thumbnail' in page:
                        return page['thumbnail']
                
            return None
        
        return None
    
    @classmethod
    def get_summary(cls) -> str:
        response = requests.get(cls.api_url(), params={
            'exintro': True,
            'action': 'query',
            'format': 'json',
            'redirects': True,
            'prop': 'extracts',
            'formatversion': 2,
            'titles': cls.search,
            'explaintext': True,
        })

        if response.status_code == HTTPStatus.OK:
            data = response.json()
            pages = data['query']['pages']
            
            if pages:
                page = pages[0]
                paragraphs = page['extract']
                
                if cls.short_summary:
                    return paragraphs.split('\n')[0]
                
                return paragraphs
            
            return None
            
        return None

    @classmethod
    def get_url(cls) -> str:
        response = requests.get(cls.api_url(), params={
            'prop': 'info',
            'inprop': 'url',
            'format': 'json',
            'action': 'query',
            'titles': cls.search,
            'formatversion': 2,
        })

        if response.status_code == HTTPStatus.OK:
            data = response.json()
            pages = data['query']['pages']
            
            if pages:
                return pages[0]['fullurl']
            
            return None
        
        return None

    @classmethod
    def get_title(cls) -> str:
        response = requests.get(cls.api_url(), params={
            'action': 'query',
            'format': 'json',
            'titles': cls.search,
        })

        if response.status_code == HTTPStatus.OK:
            data = response.json()
            pages = data['query']['pages']
            
            if pages:
                page = next(iter(pages.values()))
                return page.get('title')
            
            return None
        
        return None

    @classmethod
    def get(cls) -> dict:
        if cls.validate_location() == 'location_valid':
            return {
                'title': cls.get_title(),
                'page_url': cls.get_url(),
                'summary': cls.get_summary(),
                'thumbnail': cls.get_thumbnail(),
            }
        
        return {
            'success': False,
            'error': 'Wikipedia region is invalid',
        }
