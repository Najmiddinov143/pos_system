import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.token = None
    
    def set_token(self, token):
        self.token = token
    
    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, json=data, headers=self._headers(), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            print("❌ Serverga ulanish mumkin emas!")
            return None
        except Exception as e:
            print(f"❌ Xatolik: {e}")
            return None
    
    def get(self, endpoint):
        return self._request("GET", endpoint)
    
    def post(self, endpoint, data=None):
        return self._request("POST", endpoint, data)
    
    def login(self, username, password):
        result = self.post("/api/auth/login", {"username": username, "password": password})
        if result and "token" in result:
            self.set_token(result["token"])
        return result

api = APIClient("http://localhost:8000")