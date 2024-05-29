from flask import Flask, jsonify, url_for

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
        base_url = url_for('index', _external=True)

        for rule in cls.app.url_map.iter_rules():
            if rule.endpoint != 'index' and rule.endpoint != 'static' and rule.endpoint != 'json':
                fmt_endpoint = rule.endpoint.replace(
                    '_', '-'
                )
                
                endpoints.append({
                    'name': rule.endpoint,
                    'url': f'{base_url}{fmt_endpoint}',
                    'wiki': f'https://github.com/{cls.github}/{cls.repo}/wiki/{rule.endpoint}',
                })

        list_sorted = sorted(
            endpoints, key=lambda x: x['name']
        )
        
        return jsonify({
            'list': list_sorted,      
            'total': len(endpoints)
        })
