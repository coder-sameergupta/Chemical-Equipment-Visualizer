import requests

BASE_URL = "http://localhost:8000/api/"

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def login(self, username, password):
        try:
            response = self.session.post(BASE_URL + "login/", json={
                'username': username, 
                'password': password
            })
            if response.status_code == 200:
                self.token = response.json()['token']
                # Update session headers for future requests
                self.session.headers.update({'Authorization': f'Token {self.token}'})
                return True
            return False
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def register(self, username, email, password):
        try:
            response = self.session.post(BASE_URL + "register/", json={
                'username': username,
                'email': email,
                'password': password
            })
            return response.status_code == 201
        except Exception as e:
            print(f"Registration failed: {e}")
            return False

    def reset_password_request(self, email):
        try:
            response = self.session.post(BASE_URL + "password-reset/", json={'email': email})
            return response.status_code == 200
        except Exception as e:
            print(f"Password reset request failed: {e}")
            return False

    def get_users(self):
        try:
            response = self.session.get(BASE_URL + "users/")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def upload_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                # Authorization header is already in session if logged in
                response = self.session.post(BASE_URL + "upload/", files=files)
            return response.json() if response.status_code == 201 else None
        except Exception as e:
            print(f"Upload failed: {e}")
            return None

    def get_history(self):
        try:
            response = self.session.get(BASE_URL + "history/")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def get_summary(self, upload_id):
        try:
            response = self.session.get(BASE_URL + f"summary/{upload_id}/")
            return response.json() if response.status_code == 200 else None
        except:
            return None

    def get_data(self, upload_id):
        try:
            response = self.session.get(BASE_URL + f"data/{upload_id}/")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def download_report(self, upload_id, save_path):
        try:
            # Use stream=True for large files
            with self.session.get(BASE_URL + f"report/{upload_id}/", stream=True) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False
