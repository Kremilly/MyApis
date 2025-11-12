import os, requests, logging

from flask import jsonify
from http import HTTPStatus
from dotenv import load_dotenv

class GitHub:
    
    def __init__(self, params):
        load_dotenv()
        self.user = params.get('user')
        self.token = os.environ.get('GH_TOKEN')

    def get_query_graphql(self):
        return f"""
        query {{
            user(login: "{self.user}") {{
            pinnedItems(first: 10, types: REPOSITORY) {{
                nodes {{
                ... on Repository {{
                    name
                    description
                    url
                    homepageUrl
                    languages(first: 5, orderBy: {{field: SIZE, direction: DESC}}) {{
                        nodes {{ name }}
                    }}
                    stargazerCount
                    forkCount
                    repositoryTopics(first: 5) {{
                    nodes {{
                        topic {{ name }}
                    }}
                    }}
                    issues {{ totalCount }}
                    defaultBranchRef {{
                    target {{
                        ... on Commit {{
                        history {{ totalCount }}
                        }}
                    }}
                    }}
                    collaborators {{ totalCount }}
                }}
                }}
            }}
            }}
        }}
        """

    def user_exists(self):
        try:
            response = requests.get(f"https://api.github.com/users/{self.user}", headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json"
            })

            return response.status_code == HTTPStatus.OK

        except requests.RequestException as e:
            logging.error(f"Request Exception: {e}")
            return False

    def get_pinned_repositories(self):
        if not self.user_exists():
            logging.error(f"User '{self.user}' does not exist on GitHub")
            return HTTPStatus.NOT_FOUND

        response = requests.post("https://api.github.com/graphql", json={
            "query": self.get_query_graphql()
        }, headers={
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        })

        if response.status_code != HTTPStatus.OK:
            logging.error(f"GitHub GraphQL Error: {response.status_code}, {response.text}")
            return None

        user_data = response.json().get("data", {}).get("user")
        if not user_data:
            logging.error("User data not found in response.")
            return None

        repos = user_data.get("pinnedItems", {}).get("nodes", [])

        if repos := [repo for repo in repos if repo]:
            return [
                {
                    "name": repo.get("name"),
                    "description": repo.get("description", ""),
                    "url": repo.get("url"),
                    "home": repo.get("homepageUrl", ""),
                    "languages": [lang.get("name") for lang in repo.get("languages", {}).get("nodes", [])],
                    "stars": repo.get("stargazerCount", 0),
                    "forks": repo.get("forkCount", 0),
                    "tags": [topic.get("topic", {}).get("name", "") for topic in repo.get("repositoryTopics", {}).get("nodes", [])],
                    "issues": repo.get("issues", {}).get("totalCount", 0),
                    "commits": repo.get("defaultBranchRef", {}).get("target", {}).get("history", {}).get("totalCount", 0),
                    "contributors": (repo.get("collaborators") or {}).get("totalCount", 0)
                }
                for repo in user_data.get("pinnedItems", {}).get("nodes", [])
                if repo is not None
            ]

    def get(self):
        if not self.user:
            return jsonify({"error": "Parameter 'user' not provided"}), 400

        repositories = self.get_pinned_repositories()

        if repositories == HTTPStatus.NOT_FOUND:
            return jsonify({"error": f"User '{self.user}' does not exist on GitHub"}), 404
        elif repositories is None:
            return jsonify({"error": "Error fetching pinned repositories"}), 500
        elif len(repositories) == 0:
            return jsonify({"message": "User has no pinned repositories."}), 200

        return jsonify(repositories), 200
