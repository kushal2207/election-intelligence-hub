"""
Backend Integration Test Suite
Tests all API endpoints of the India Election Knowledge Graph Assistant.
"""

import httpx
import json
import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
JWT_SECRET = os.getenv("JWT_SECRET")

def create_test_token(role="viewer"):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "test-user-001",
        "email": "test@example.com",
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=24),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def run_tests():
    token = create_test_token()
    auth_headers = {"Authorization": f"Bearer {token}"}
    passed = 0
    failed = 0

    # ---------------------------------------------------------------
    # TEST 1: Health check
    # ---------------------------------------------------------------
    print("=" * 60)
    print("TEST 1: GET /health")
    print("=" * 60)
    r = httpx.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    body = r.json()
    assert body["status"] == "ok"
    print(f"  Status: {r.status_code}  Body: {body}")
    print("  PASSED ✓")
    passed += 1
    print()

    # ---------------------------------------------------------------
    # TEST 2: OpenAPI schema available
    # ---------------------------------------------------------------
    print("=" * 60)
    print("TEST 2: GET /openapi.json")
    print("=" * 60)
    r = httpx.get(f"{BASE_URL}/openapi.json")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    spec = r.json()
    paths = list(spec.get("paths", {}).keys())
    print(f"  Available paths: {paths}")
    print(f"  Title: {spec.get('info', {}).get('title')}")
    print(f"  Version: {spec.get('info', {}).get('version')}")
    print("  PASSED ✓")
    passed += 1
    print()

    # ---------------------------------------------------------------
    # TEST 3: Query without auth → 401
    # ---------------------------------------------------------------
    print("=" * 60)
    print("TEST 3: POST /api/v1/query (NO AUTH → expect 401)")
    print("=" * 60)
    query_payload = {
        "query_text": "What are the election rules?",
        "user_location": {
            "jurisdiction_id": "test-jurisdiction-001",
            "constituency_id": "test-constituency-001",
        },
        "user_language": "en",
    }
    r = httpx.post(f"{BASE_URL}/api/v1/query", json=query_payload)
    print(f"  Status: {r.status_code}")
    if r.status_code == 401:
        print("  PASSED ✓  (correctly rejected unauthenticated request)")
        passed += 1
    else:
        print(f"  FAILED ✗  (expected 401, got {r.status_code})")
        failed += 1
    print()

    # ---------------------------------------------------------------
    # TEST 4: Invalid payload → 422
    # ---------------------------------------------------------------
    print("=" * 60)
    print("TEST 4: POST /api/v1/query (INVALID PAYLOAD → expect 422)")
    print("=" * 60)
    r = httpx.post(f"{BASE_URL}/api/v1/query", json={"bad": "data"}, headers=auth_headers)
    print(f"  Status: {r.status_code}")
    if r.status_code == 422:
        print("  PASSED ✓  (correctly rejected invalid payload)")
        passed += 1
    else:
        print(f"  FAILED ✗  (expected 422, got {r.status_code})")
        failed += 1
    print()

    # ---------------------------------------------------------------
    # TEST 5: Expired token → 401
    # ---------------------------------------------------------------
    print("=" * 60)
    print("TEST 5: POST /api/v1/query (EXPIRED TOKEN → expect 401)")
    print("=" * 60)
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": "test-user-001",
        "email": "test@example.com",
        "role": "viewer",
        "iat": now - timedelta(hours=48),
        "exp": now - timedelta(hours=24),
    }
    expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm="HS256")
    r = httpx.post(
        f"{BASE_URL}/api/v1/query",
        json=query_payload,
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 401:
        print("  PASSED ✓  (correctly rejected expired token)")
        passed += 1
    else:
        print(f"  FAILED ✗  (expected 401, got {r.status_code})")
        failed += 1
    print()

    # ---------------------------------------------------------------
    # TEST 6: Authenticated query (full pipeline)
    # ---------------------------------------------------------------
    print("=" * 60)
    print("TEST 6: POST /api/v1/query (AUTHENTICATED → full pipeline)")
    print("=" * 60)
    r = httpx.post(
        f"{BASE_URL}/api/v1/query",
        json=query_payload,
        headers=auth_headers,
        timeout=60,
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        resp = r.json()
        print(f"  Response status: {resp.get('status')}")
        print(f"  Confidence: {resp.get('confidence')}")
        print(f"  Conflict detected: {resp.get('conflict_detected')}")
        print(f"  Source citations: {len(resp.get('source_citations', []))}")
        print(f"  Execution trace:")
        for t in resp.get("execution_trace", []):
            print(f"    → {t}")
        answer = resp.get("final_answer", "")
        preview = answer[:400] + "..." if len(answer) > 400 else answer
        print(f"  Answer preview:\n    {preview}")
        print("  PASSED ✓")
        passed += 1
    else:
        print(f"  FAILED ✗  Body: {r.text[:500]}")
        failed += 1
    print()

    # ---------------------------------------------------------------
    # TEST 7: Hindi query + translation
    # ---------------------------------------------------------------
    print("=" * 60)
    print("TEST 7: POST /api/v1/query (Hindi translation)")
    print("=" * 60)
    hindi_payload = {
        "query_text": "भारत में चुनाव कैसे होते हैं?",
        "user_location": {
            "jurisdiction_id": "test-jurisdiction-001",
            "constituency_id": "test-constituency-001",
        },
        "user_language": "hi",
    }
    r = httpx.post(
        f"{BASE_URL}/api/v1/query",
        json=hindi_payload,
        headers=auth_headers,
        timeout=60,
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        resp = r.json()
        print(f"  Response status: {resp.get('status')}")
        print(f"  Execution trace:")
        for t in resp.get("execution_trace", []):
            print(f"    → {t}")
        answer = resp.get("final_answer", "")
        preview = answer[:400] + "..." if len(answer) > 400 else answer
        print(f"  Answer preview:\n    {preview}")
        print("  PASSED ✓")
        passed += 1
    else:
        print(f"  FAILED ✗  Body: {r.text[:500]}")
        failed += 1
    print()

    # ---------------------------------------------------------------
    # TEST 8: Auth endpoints exist
    # ---------------------------------------------------------------
    print("=" * 60)
    print("TEST 8: GET /auth/login (OAuth redirect)")
    print("=" * 60)
    r = httpx.get(f"{BASE_URL}/auth/login", follow_redirects=False)
    print(f"  Status: {r.status_code}")
    if r.status_code in (302, 307, 200):
        print("  PASSED ✓  (auth login endpoint responds)")
        passed += 1
    else:
        print(f"  FAILED ✗  (unexpected status {r.status_code})")
        failed += 1
    print()

    # ---------------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------------
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
