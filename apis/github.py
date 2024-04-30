import os, requests, logging

from dotenv import load_dotenv

from http import HTTPStatus

from flask import jsonify

class GitHub:
    
    @classmethod
    def __init__(cls, params):
        cls.user = params['user']
        
    @classmethod
    def get_query_graphql(cls, username):
        return """
        query {
            user(login: "%s") {
                pinnedItems(first: 10, types: REPOSITORY) {
                    nodes {
                        ... on Repository {
                            name
                            description
                            url
                            homepageUrl
                            languages(first: 5) {
                                nodes { name }
                            }
                            stargazerCount
                            forkCount
                            repositoryTopics(first: 5) {
                                nodes {
                                    topic { name }
                                }
                            }
                            issues {
                                totalCount
                            }
                            defaultBranchRef {
                                target {
                                    ... on Commit {
                                        history { totalCount }
                                    }
                                }
                            }
                            collaborators { totalCount }
                        }
                    }
                }
            }
        }
        """ % username
    
    @classmethod
    def user_exists(cls, username, token):
        try:
            response = requests.get(f"https://api.github.com/users/{username}", headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json"
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
    def get_pinned_repositories(cls, username, token):
        if not cls.user_exists(username, token):
            logging.error(f"User '{username}': does not exist on GitHub")
            return 404

        try:
            response = requests.post("https://api.github.com/graphql", json={
                "query": cls.get_query_graphql(username)
            }, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            })
            
            response.raise_for_status()

            if response.status_code == HTTPStatus.OK:
                data = response.json().get("data", {}).get("user", {})
                
                return [
                    {
                        "name": repo["name"],
                        "description": repo["description"],
                        "url": repo["url"],
                        "home": repo.get("homepageUrl", ""),
                        "languages": [
                            lang["name"] for lang in repo["languages"]["nodes"]
                        ],
                        "stars": repo.get("stargazerCount", 0),
                        "forks": repo.get("forkCount", 0),
                        "tags": [
                            topic.get("topic", {}).get("name", "") for topic in repo.get("repositoryTopics", {}).get("nodes", [])
                        ],
                        "issues": repo.get("issues", {}).get("totalCount", 0),
                        "commits": repo.get("defaultBranchRef", {}).get("target", {}).get("history", {}).get("totalCount", 0),
                        "contributors": repo.get("collaborators", {}).get("totalCount", 0)
                    }
                    
                    for repo in data.get("pinnedItems", {}).get("nodes", [])
                ]
            
            logging.error(
                f"Error retrieving pinned repositories. Status Code: {response.status_code}, Response: {response.text}"
            )
            
            return None

        except requests.RequestException as e:
            logging.error(f"Request Exception: {e}")
            return None

    @classmethod
    def get(cls):
        load_dotenv()

        if cls.user is None:
            return jsonify({
                "error": "Parameter 'user' not provided"
            }), 400
        
        callback = cls.get_pinned_repositories(
            cls.user,
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
            return jsonify(
                callback
            ), 200
            
        else:
            return jsonify({
                "error": "Error fetching pinned repositories"
            }), 500
