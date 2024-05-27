from flask import Flask, jsonify, url_for

class Kremilly:
    
    @classmethod
    def __init__(cls, app: Flask, params:dict) -> jsonify:
        cls.app = app
        cls.repo = params['repo']
        cls.github = params['github']
        
        cls.pypi = params['pypi']
        cls.crates = params['crates']
        cls.domain = params['domain']
        cls.packagist = params['packagist']
        cls.email = params['email']
    
    @classmethod
    def list_json(cls):
        endpoints = []
        base_url = url_for('index', _external=True)

        for rule in cls.app.url_map.iter_rules():
            if rule.endpoint != 'index' and rule.endpoint != 'static' and rule.endpoint != 'json':
                endpoints.append({
                    'name': rule.endpoint,
                    'url': f'{base_url}{rule.endpoint}',
                    'wiki': f'https://github.com/kremilly/MyApis/wiki/{rule.endpoint}',
                })

        list_sorted = sorted(
            endpoints, key=lambda x: x['name']
        )
        
        return jsonify({
            'list': list_sorted,      
            'total': len(endpoints)
        })
