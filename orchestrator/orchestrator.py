import os
import time
import hashlib
import secrets
from jwcrypto import jwk, jwt
import requests
import json

class Orchestrator:
    def __init__(self):
        self.keycloak_url = os.getenv('KEYCLOAK_URL', 'http://localhost:8080')
        self.api_url = os.getenv('INTERNAL_API_URL')
        self.client_id = os.getenv('CLIENT_ID', 'orchestrator')
        self.client_secret = os.getenv('CLIENT_SECRET', 'orchestrator-secret')
        self.realm = os.getenv('REALM', 'agentic-demo')

        # Generate DPoP key pair (persist for session)
        self.dpop_key = jwk.JWK.generate(kty='EC', crv='P-256')

        # Token cache
        self.cached_token = None
        self.token_expiry = 0

    def get_user_token(self):
        """Step 1: Get user access token via OAuth2 client credentials"""
        start = time.time()

        response = requests.post(
            f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        )

        elapsed = (time.time() - start) * 1000

        if response.status_code != 200:
            raise Exception(f"Failed to get user token: {response.text}")

        data = response.json()
        return data['access_token'], elapsed

    def exchange_token(self, user_token):
        """Step 2: Exchange user token for delegated token (RFC 8693) - REAL IMPLEMENTATION"""
        start = time.time()

        response = requests.post(
            f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "subject_token": user_token,
                "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "audience": "internal-api"
            }
        )

        elapsed = (time.time() - start) * 1000

        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")

        data = response.json()
        return data['access_token'], elapsed

    def generate_dpop_proof(self, method, url, access_token):
        """Step 3: Generate DPoP proof (RFC 9449)"""
        start = time.time()

        # Compute access token hash
        ath = hashlib.sha256(access_token.encode('utf-8')).hexdigest()

        # Create DPoP JWT
        header = {
            "typ": "dpop+jwt",
            "alg": "ES256",
            "jwk": json.loads(self.dpop_key.export_public())
        }

        claims = {
            "jti": secrets.token_urlsafe(16),
            "htm": method,
            "htu": url,
            "iat": int(time.time()),
            "ath": ath
        }

        dpop_token = jwt.JWT(
            header=header,
            claims=claims
        )
        dpop_token.make_signed_token(self.dpop_key)

        elapsed = (time.time() - start) * 1000

        return dpop_token.serialize(), elapsed

    def call_api(self, access_token, dpop_proof):
        """Step 4: Call internal API with DPoP-bound token"""
        start = time.time()

        response = requests.get(
            f"{self.api_url}/api/resource",
            headers={
                "Authorization": f"Bearer {access_token}",
                "DPoP": dpop_proof
            }
        )

        elapsed = (time.time() - start) * 1000

        return response, elapsed

    def run_request(self, use_cache=False):
        """Execute complete request flow with measurements"""
        metrics = {
            "token_exchange_ms": 0,
            "dpop_sign_ms": 0,
            "api_call_ms": 0,
            "server_verify_ms": 0,
            "end_to_end_ms": 0,
            "status": 0
        }

        start_total = time.time()

        try:
            # Get/exchange token
            if use_cache and self.cached_token and time.time() < self.token_expiry:
                access_token = self.cached_token
                metrics["token_exchange_ms"] = 0  # Using cache
            else:
                user_token, get_token_time = self.get_user_token()
                access_token, exchange_time = self.exchange_token(user_token)
                metrics["token_exchange_ms"] = exchange_time

                # Cache token
                self.cached_token = access_token
                self.token_expiry = time.time() + 240  # 4 minutes (5 min token - 1 min buffer)

            # Generate DPoP proof
            dpop_proof, dpop_time = self.generate_dpop_proof(
                "GET",
                f"{self.api_url}/api/resource",
                access_token
            )
            metrics["dpop_sign_ms"] = dpop_time

            # Call API
            response, api_time = self.call_api(access_token, dpop_proof)
            metrics["api_call_ms"] = api_time
            metrics["status"] = response.status_code

            # Extract server metrics if available
            if response.status_code == 200:
                data = response.json()
                metrics["server_verify_ms"] = data.get("server_verify_ms", 0)

        except Exception as e:
            print(f"Request failed: {e}")
            metrics["status"] = 500

        metrics["end_to_end_ms"] = (time.time() - start_total) * 1000

        return metrics


if __name__ == '__main__':
    # Quick test
    print("Testing Real Token Exchange with Keycloak 26.2...")
    print("=" * 50)

    orch = Orchestrator()

    try:
        # Test 1: Get subject token
        print("\n[1/3] Getting subject token...")
        subject_token, _ = orch.get_user_token()
        print(f"✓ Subject token: {subject_token[:50]}...")

        # Test 2: Exchange token
        print("\n[2/3] Exchanging token (RFC 8693)...")
        exchanged_token, exchange_ms = orch.exchange_token(subject_token)
        print(f"✓ Exchanged token: {exchanged_token[:50]}...")
        print(f"✓ Exchange time: {exchange_ms:.2f}ms")

        # Test 3: Generate DPoP
        print("\n[3/3] Generating DPoP proof...")
        dpop, dpop_ms = orch.generate_dpop_proof("GET", "http://test", exchanged_token)
        print(f"✓ DPoP proof generated")
        print(f"✓ DPoP time: {dpop_ms:.2f}ms")

        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print(f"Total measured overhead: {exchange_ms + dpop_ms:.2f}ms")

    except Exception as e:
        print(f"\n❌ Error: {e}")
