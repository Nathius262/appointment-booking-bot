import requests
import base64

# Test /api with an image file
file_path = "../FastAPI/images/1722243709.5747457.png"
with open(file_path, "rb") as f:
    files = {"data": f}
    response = requests.post("http://localhost:8888/api", files=files)

print(response.json())

# Test /api_base64 with a base64-encoded image
with open(file_path, "rb") as f:
    b64_data = base64.b64encode(f.read()).decode("utf-8")

payload = {"data": b64_data}
response = requests.post("http://localhost:8888/api_base64", json=payload)

print(response.json())


### run api
###  uvicorn run:app --host 0.0.0.0 --port 8888 --workers 2 --reload --log-level debug