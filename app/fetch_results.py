import requests
import json
from mpulse_session_manager import MPulseSessionManager
import base64

class Process:
    @staticmethod
    def decode_base64_from_dict(data):
        try:
            # Extracting the base64 encoded result
            encoded_result = data.get("result")
            if not encoded_result:
                return "No 'result' field found in the provided data."

            # Decoding the base64 encoded string
            decoded_result = base64.b64decode(encoded_result).decode('utf-8')
            return decoded_result
        except Exception as e:
            return f"An error occurred during decoding: {e}"
        
class MPulseAPI:
    def __init__(self, base_url="https://mpulse.maybanksandbox.com"):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json'
        }

    def make_request(self, method, params):
        url = f"{self.base_url}/index.php/admin/remotecontrol"
        payload = json.dumps({
            "method": method,
            "params": params,
            "id": 1
        })

        response = requests.post(url, headers=self.headers, data=payload)

        return response

# # get session key
# username = "pluginManager"
# password = "w4Gu6ctRvCHm"
# session = MPulseSessionManager(username, password, base_url="https://mpulse-dev.maybanksandbox.com")
# session_key = session.get_session_key()

# # run api to get survey responses

# api = MPulseAPI()
# method = "export_responses"
# params = [session_key, 957272, "csv", "en", "complete"]

# response = api.make_request(method, params)
# response_data = response.json()
# results = Process.decode_base64_from_dict(response_data)
# # print(results)

# if response.status_code == 200:
#     print(response.text)
# else:
#     print("Request failed with status code", response.status_code)
