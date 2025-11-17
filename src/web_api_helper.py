"""
This module provides helps in fetching public GitHub gists for a user.
It validates the GitHub username and
returns list of public gists using the GitHub API.

"""

from urllib.parse import urlparse, parse_qs
from http import HTTPStatus
import requests


# ---- Configuration Constants ----
GITHUB_API_BASE_URL = "https://api.github.com/users"
GITHUB_API_VERSION = "2022-11-28"
DEFAULT_PAGE = 1
PER_PAGE = 50
REQUEST_TIMEOUT = 20

# ---- HTTP status codes ----
HTTP_OK = HTTPStatus.OK
BAD_REQUEST = HTTPStatus.BAD_REQUEST
HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND
SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR

# ---- Cache ----
gist_cache = {}

# ---- Usage ----
USAGE = "Usage - 127.0.0.1:8080/USERNAME[?page=NUMBER]"


class GithubAPIClient:
    """Client to interact with GitHub API"""

    def __init__(self, base_url=GITHUB_API_BASE_URL, timeout=REQUEST_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout

    def get_user_gists(self, username, page=DEFAULT_PAGE, per_page=PER_PAGE):
        """Fetch public gists for a given GitHub username"""
        url = f"{self.base_url}/{username}/gists"
        params = {"per_page": per_page, "page": page}
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": GITHUB_API_VERSION
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


class GistsBuilder:
    """Builds json response for gists"""

    @staticmethod
    def response(username, gists, page):
        """ returns public gists lists"""
        public_gists_lists = {
            'name': username,
            'page': page,
            'total_gists': len(gists),
            'gists_list': []
        }

        for gist in gists:
            if "html_url" in gist:
                gist_info = {
                    "id": gist.get("id"),
                    "description": gist.get("description") or "No Description",
                    "html_url": gist.get("html_url"),
                    "files": list(gist.get("files", {}).keys())
                }
                public_gists_lists['gists_list'].append(gist_info)
        return public_gists_lists

    @staticmethod
    def error(message):
        """ returns error message"""
        return {'error': message}


class GetPublicGistsService:
    """Service to fetch public gists for a GitHub user"""

    def __init__(self, path: str):
        self.api_client = GithubAPIClient()
        self.username, self.page = self._parse_request_path(path)
        self.cache_key = f"{self.username}_{self.page}"

    def handle_request(self):
        """ Validate the request and returns gist data or error message """
        if self.username == "favicon.ico":
            return HTTP_OK, None

        if self.username is None or self.page is None:
            return BAD_REQUEST, GistsBuilder.error(USAGE)

        gists = gist_cache.get(self.cache_key)
        if gists:
            return HTTP_OK, GistsBuilder.response(self.username, gists, self.page)

        return self._fetch_and_cache_gists()

    def _parse_request_path(self, path: str):
        """Parse the request path to extract user and query parameters"""
        parsed_url = urlparse(path)
        path_parts = parsed_url.path.strip("/").split("/")
        username = path_parts[0]

        if not username or len(path_parts) != 1:
            return None, None

        query_params = parse_qs(parsed_url.query, keep_blank_values=True)
        non_page_keys = any(k != "page" for k in query_params)
        page_str = query_params.get("page", [str(DEFAULT_PAGE)])[0]
        if not page_str.isdigit() or int(page_str) < 1 or non_page_keys:
            return username, None

        return username, int(page_str)

    def _fetch_and_cache_gists(self):
        """Fetch gists from GitHub API and cache the result"""
        try:
            gists = self.api_client.get_user_gists(self.username, self.page)
            gist_cache[self.cache_key] = gists
            fmt_gists = GistsBuilder.response(self.username, gists, self.page)
            return HTTP_OK, fmt_gists

        except requests.exceptions.HTTPError as http_err:
            if (
                http_err.response is not None and
                http_err.response.status_code == HTTP_NOT_FOUND
            ):
                return HTTP_NOT_FOUND, GistsBuilder.error("User not found.")
            return SERVER_ERROR, GistsBuilder.error(f"HTTP error: {str(http_err)}")

        except ValueError:
            return SERVER_ERROR, GistsBuilder.error("Invalid JSON response")

        except requests.exceptions.RequestException as req_err:
            return SERVER_ERROR, GistsBuilder.error(f"{str(req_err)}")
