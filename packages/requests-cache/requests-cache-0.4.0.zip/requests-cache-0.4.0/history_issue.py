import requests

resp = requests.get("http://httpbin.org/redirect/4")
for r in resp.history:
    print("url: {} request.url: {}".format(r.url, r.request.url))