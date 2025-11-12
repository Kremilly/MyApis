import json
from flask import Flask, jsonify, request, Response

class Kremilly:
    
    @classmethod
    def __init__(cls, app: Flask, params:dict) -> jsonify:
        cls.app = app
        
        cls.repo = params['repo']
        cls.github = params['github']
        cls.domain = params['domain']
    
    @classmethod
    def list_json(cls):
        endpoints = []
        base_url = request.url_root

        for rule in cls.app.url_map.iter_rules():
            if rule.endpoint != 'index' and rule.endpoint != 'static' and rule.endpoint != 'json' and rule.endpoint != 'rss':
                fmt_endpoint = rule.endpoint.replace(
                    '_', '-'
                ).replace(
                    '//', '/'
                )
                
                endpoints.append({
                    'name': rule.endpoint,
                    'url': f'{base_url}{fmt_endpoint}',
                    'wiki': f'https://{cls.domain}/{rule.endpoint}',
                })

        list_sorted = sorted(
            endpoints, key=lambda x: x['name']
        )
        
        return jsonify({
            'list': list_sorted,      
            'total': len(endpoints)
        })
    
    @classmethod
    def rss(cls):
        rss_items = ''
        base_url = request.url_root
        
        response = cls.list_json()
        list_apis = response.data.decode('utf-8')
        data = json.loads(list_apis)

        for api in data['list']:
            rss_items += f"""<item>
                <title>{api['name']}</title>
                <link>{api['wiki']}</link>
                <uri>{api['url']}</uri>
            </item>"""
        
        return Response(
            f"""<?xml version="1.0" encoding="UTF-8" ?>
            <rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/" >
                <channel>
                    <title>{cls.github}: API's</title>
                    <link>{base_url}</link>
                    <language>en-us</language>
                    {rss_items}
                </channel>
            </rss>""", mimetype='application/xml'
        )
        