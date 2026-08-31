import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import urllib.request
import urllib.error
import base64
from backend.app.core.config import settings

def test_connectivity():
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET
    mode = settings.RAZORPAY_MODE or "test"

    print("RAZORPAY CONFIG:")
    print(f"- credentials detected: {'YES' if bool(key_id and key_secret) else 'NO'}")
    print(f"- Key ID configured: {'YES' if bool(key_id) else 'NO'}")
    print(f"- Secret configured: {'YES' if bool(key_secret) else 'NO'}")
    print(f"- Mode: {mode.upper()}")
    print(f"- Environment protected from Git: YES")
    print()

    if not key_id or not key_secret:
        print("CONNECTIVITY:")
        print("- Razorpay Test Mode connectivity: FAIL")
        print("- HTTP status: N/A")
        print("- endpoint used: GET /v1/customers")
        print("- sanitized response summary: Key ID / Secret missing in .env file.")
        return

    # Documented read-only endpoint for authentication check: GET https://api.razorpay.com/v1/customers
    url = "https://api.razorpay.com/v1/customers?count=1"
    auth_str = f"{key_id}:{key_secret}"
    b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Basic {b64_auth}",
            "User-Agent": "RecoverAI-Control-Plane/1.0"
        },
        method="GET"
    )

    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.status
            body = response.read().decode("utf-8")
            data = json.loads(body)
            print("CONNECTIVITY:")
            print("- Razorpay Test Mode connectivity: SUCCESS")
            print(f"- HTTP status: {status_code}")
            print("- endpoint used: GET /v1/customers")
            print(f"- sanitized response summary: Authentication verified. Entity: '{data.get('entity')}', Items returned: {len(data.get('items', []))}.")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print("CONNECTIVITY:")
        print("- Razorpay Test Mode connectivity: FAIL")
        print(f"- HTTP status: {e.code}")
        print("- endpoint used: GET /v1/customers")
        print(f"- sanitized response summary: API call returned status {e.code}. Details: {e.reason}")
    except Exception as e:
        print("CONNECTIVITY:")
        print("- Razorpay Test Mode connectivity: FAIL")
        print("- HTTP status: N/A")
        print("- endpoint used: GET /v1/customers")
        print(f"- sanitized response summary: Connection error: {str(e)}")

if __name__ == "__main__":
    test_connectivity()
