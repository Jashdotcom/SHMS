"""Live smoke tests against a running SHMS dev server."""

import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen, HTTPCookieProcessor, build_opener

BASE = "http://127.0.0.1:8000"
ISSUES = []


def record(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        ISSUES.append(f"{name}: {detail}")


def _csrf_from_html(html):
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html.decode("utf-8", errors="ignore"))
    return match.group(1) if match else ""


def main():
    opener = build_opener(HTTPCookieProcessor())

    def get(path, expected=(200, 302)):
        req = Request(BASE + path, method="GET")
        try:
            resp = opener.open(req)
            return resp.getcode(), resp.read()
        except HTTPError as exc:
            if exc.code in expected:
                return exc.code, exc.read()
            raise

    def post(path, data=None, json_body=None, expected=(200, 302), referer=None):
        headers = {}
        payload = None
        if json_body is not None:
            payload = json.dumps(json_body).encode()
            headers["Content-Type"] = "application/json"
        elif data is not None:
            payload = urlencode(data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        if referer:
            headers["Referer"] = referer
        req = Request(BASE + path, data=payload, headers=headers, method="POST")
        try:
            resp = opener.open(req)
            return resp.getcode(), resp.read()
        except HTTPError as exc:
            if exc.code in expected:
                return exc.code, exc.read()
            raise

    try:
        code, _ = get("/", expected=(302,))
        record("Home redirect (anonymous)", code == 302, f"status={code}")
    except URLError as exc:
        record("Server reachable", False, str(exc))
        print("\nServer not running at", BASE)
        return 1

    login_page_code, login_html = get("/login")
    csrf = _csrf_from_html(login_html)
    code, _ = post(
        "/login",
        {"username": "admin", "password": "admin123", "csrfmiddlewaretoken": csrf},
        expected=(200, 302),
        referer=BASE + "/login",
    )
    record("Admin login", code in (200, 302), f"status={code}")

    for path in ["/dashboard", "/analytics", "/rooms", "/bookings/history", "/payments", "/announcements", "/admin-complaints/"]:
        try:
            code, _ = get(path)
            record(f"Admin GET {path}", code == 200, f"status={code}")
        except HTTPError as exc:
            record(f"Admin GET {path}", False, f"status={exc.code}")

    code, body = post("/api/token/", json_body={"username": "admin", "password": "admin123"}, expected=(200,))
    record("JWT token", code == 200, f"status={code}")
    token = json.loads(body.decode()).get("access", "")
    req = Request(BASE + "/api/rooms/", headers={"Authorization": f"Bearer {token}"})
    code = opener.open(req).getcode()
    record("JWT API /api/rooms/", code == 200, f"status={code}")

    paid = None
    req = Request(BASE + "/api/payments/", headers={"Authorization": f"Bearer {token}"})
    payments = json.loads(opener.open(req).read().decode()).get("results", [])
    for item in payments:
        if item.get("status") == "paid":
            paid = item["id"]
            break
    if paid:
        code, body = get(f"/receipt/{paid}/")
        record("Invoice PDF download", code == 200 and body.startswith(b"%PDF"), f"status={code}")
    else:
        record("Invoice PDF download", False, "no paid payment in seed data")

    print(f"\nLive smoke summary: {len(ISSUES)} issue(s)")
    for issue in ISSUES:
        print(" -", issue)
    return 1 if ISSUES else 0


if __name__ == "__main__":
    sys.exit(main())
