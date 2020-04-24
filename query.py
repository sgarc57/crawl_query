#!/usr/bin/env python3
from flask import Flask, request
from bs4 import BeautifulSoup
import re
import json
import requests


app = Flask(__name__)

SITE_STRING = "https://{site}/{query}"


@app.route("/query", methods=["POST"])
def query():
    messages = []
    if request.method == "GET":
        messages.append("received GET request")
        return json.dumps({"get": "ok", "messages": messages}, indent=4)
    elif request.method == "POST":
        messages.append("received POST request")
        data = json.loads(request.data)
        if "site" and "query" in data:
            messages.append(
                "site: {site} found in data and query: {query} foud in request".format(
                    site=data["site"], query=data["query"]
                )
            )
            try:
                generated_url = SITE_STRING.format(site=data["site"], query=data["query"])
                r = requests.get(generated_url, verify=False)
                if r.status_code == 200:
                    messages.append(
                        "request to: https://{}/{} produced: {}".format(data["site"], data["query"], str(r.status_code))
                    )
                else:
                    messages.append(
                        "request to: https://{}/{} produced: {}".format(data["site"], data["query"], str(r.status_code))
                    )
            except Exception as e:
                messages.append("request failed, error: {}".format(e))

            try:
                soup = BeautifulSoup(r.content, "html.parser")
                links = soup.body.findAll("a")
                hrefs = []
                for link in links:
                    hrefs.append(link.attrs["href"])

                hrefs_reg = []
                for item in hrefs:
                    searchObj = re.search(r"http.*", item, re.I)
                    if searchObj:
                        hrefs_reg.append(searchObj.group())

                hrefs_mag = []
                for mag in hrefs:
                    searchObj = re.search(r"magnet.*", mag, re.I)
                    if searchObj:
                        hrefs_mag.append(searchObj.group())
                messages.append({"soup": "parsed", "links": hrefs, "urls": hrefs_reg, "magnet links": hrefs_mag})
            except:
                soup = {"status": "failed to parse"}
                messages.append({"soup": soup})
        elif "site" in data:
            messages.append("only site {} found in data".format(data["site"]))
        elif "query" in data:
            messages.append("only query {} found in data".format(data["query"] ))

        return json.dumps({"post": "ok", "messages": messages}, indent=4)


@app.route("/")
def index():
    return "Hello, I make requests", 200


# We only need this for local development.
if __name__ == "__main__":
    app.run()
