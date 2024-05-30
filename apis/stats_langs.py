import os, requests, logging

from flask import jsonify
from http import HTTPStatus
from dotenv import load_dotenv

class GitHubStatsLangs:
    
    @classmethod
    def __init__(cls, params):
        cls.user = params['user']
        cls.is_fork = bool(params['forks']) if params['forks'] else False
        
    @classmethod
    def get_query_graphql(cls, is_fork):
        fork_query = ""
        
        if not is_fork:
            fork_query = ", ownerAffiliations: OWNER, isFork: false"
            
        return f"""
            query($username: String!) {{
                user(login: $username) {{
                    repositories(first: 100 {fork_query}) {{
                        totalCount
                        nodes {{
                            primaryLanguage {{ name }}
                        }}
                    }}
                }}
            }}
        """
    
    @classmethod
    def user_exists(cls, username, is_token, token):
        try:
            response = requests.post('https://api.github.com/graphql', json={
                'query': cls.get_query_graphql(is_token), 
                'variables': {
                    'username': username
                }
            }, headers={
                'Authorization': f'Bearer {token}'
            })
            
            if response.status_code == HTTPStatus.OK:
                return True
            elif response.status_code == HTTPStatus.NOT_FOUND:
                return False
            else:
                logging.error(f"Failed to check if user exists. Status Code: {response.status_code}, Response: {response.text}")
                return False
            
        except requests.RequestException as e:
            logging.error(f"Request Exception: {e}")
            return False
      
    @classmethod  
    def get_github_languages(cls, username, is_fork, token):
        if not cls.user_exists(username, is_fork, token):
            logging.error(f"User '{username}': does not exist on GitHub")
            return 404
        
        response = requests.post('https://api.github.com/graphql', json={
            'query': cls.get_query_graphql(is_fork),
            'variables': {
                'username': username
            }
        }, headers={
            'Authorization': f'Bearer {token}'
        })

        language_count = {}
        repositories = response.json()['data']['user']['repositories']
        total_repos = repositories['totalCount']

        for repo in repositories['nodes']:
            primary_language = repo['primaryLanguage']
            
            if primary_language:
                language_name = primary_language['name']
                
                if language_name:
                    if language_name in language_count:
                        language_count[language_name] += 1
                    else:
                        language_count[language_name] = 1
        
        language_list = [{
            'language': lang,
            'repositories': count,
            'percentage': {
                'value': (count / total_repos) * 100,
                'formatted': f'{(count / total_repos) * 100:.0f}%',
            },
        } for lang, count in language_count.items()]
        
        return sorted(
            language_list, key=lambda x: x['repositories'], reverse=True
        )

    @classmethod
    def get(cls):
        load_dotenv()

        if cls.user is None:
            return jsonify({
                "error": "Parameter 'user' not provided"
            }), 400
        
        callback = cls.get_github_languages(
            cls.user,
            cls.is_fork,
            os.environ.get('GH_TOKEN')
        )
        
        if not callback:
            return jsonify({
                "message": f"User '{cls.user}' does not have any pinned repositories"
            }), 200
            
        elif callback == HTTPStatus.NOT_FOUND:
            return jsonify({
                "error": f"User '{cls.user}' does not exist on GitHub"
            }), 404
            
        elif callback:
            return jsonify({
                'languages': callback,
                'total': len(callback),
            }), 200
            
        else:
            return jsonify({
                "error": "Error fetching pinned repositories"
            }), 500
