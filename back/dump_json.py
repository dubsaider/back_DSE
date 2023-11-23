import requests

solditems = requests.get('http://10.63.17.70:8000/api/data/') # (your url)
data = solditems.content
with open('data.json', 'wb') as f:
    f.write(data)