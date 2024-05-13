import requests

from flask import jsonify
from http import HTTPStatus

class CVE:
    
    @classmethod
    def __init__(cls, params:dict):
        cls.cve = cls.check_cve_word_in_param(params['id'])
        
    @classmethod
    def check_cve_word_in_param(cls, cve:str) -> str:
        cve = cve.upper()
        
        if not 'CVE-' in cve:
            return f'CVE-{cve}' 
        
        return cve
    
    @classmethod
    def get_cve_data(cls, api_uri_json:str, data:dict) -> dict:
        return {
            'data_type': data['dataType'],
            'metadata': data['cveMetadata'],
            'data_version': data['dataVersion'],
            'title': data['containers']['cna']['title'],
            'source': data['containers']['cna']['source'],
            'credits': data['containers']['cna']['credits'],
            'affected': data['containers']['cna']['affected'],
            'description': data['containers']['cna']['descriptions'][0],
            'engine': data['containers']['cna']['x_generator']['engine'],
            'provider_metadata': data['containers']['cna']['providerMetadata'],
            
            'pages_url': {
                'json': api_uri_json,
                'page': f'https://www.cve.org/CVERecord?id={cls.cve}',
            },
            
            'references': [
                ref['url'] for ref in data['containers']['cna']['references']
            ],
            
            'problem_types': [
                pt['descriptions'][0] for pt in data['containers']['cna']['problemTypes']
            ][0],
            
            'metrics': [
                metric['other'] for metric in data['containers']['cna']['metrics']
            ][0],
        }
        
    @classmethod
    def get(cls):
        api_uri_json = f'https://cveawg.mitre.org/api/cve/{cls.cve}'
        response = requests.get(api_uri_json)

        if response.status_code == HTTPStatus.OK:
            data = cls.get_cve_data(
                data=response.json(),
                api_uri_json=api_uri_json, 
            )
            
            return jsonify({
                key: data[key] for key in sorted(data.keys())
            })
        else:
            return jsonify({
                'success': False,
                'status_code': response.status_code,
                'message': 'Failed to retrieve data from the API.'
            })
