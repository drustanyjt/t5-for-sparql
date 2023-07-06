import requests
import json

data = {
  "headers": {
      "Content-Type": "application/json"
  },
  "data" : {
      "text":"What is the operating income of Qantas?"
  }
}

r = requests.post("https://labs.tib.eu/falcon/falcon2/api?mode=long", json=json.dumps(data))
print(r)