import os
import time
from flask import Flask, request, jsonify
from dpop_verify import verify_dpop_proof
from jti_cache import JTICache
import jwt
import requests

app = Flask(__name__)
jti_cache = JTICache()

KEYCLOAK_URL = os.getenv('KEYCLOAK_URL')
REALM = os.getenv('REALM', 'agentic-demo')

def get_jwks():
    """Fetch JWKS from Keycloak for token verification"""
    response = requests.get(
        f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
    )
    return response.json()

def verify_access_token(token):
    """Verify OAuth access token"""
    try:
        jwks = get_jwks()

        # Decode token header to get kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        # Find matching key
        key = None
        for jwk in jwks['keys']:
            if jwk['kid'] == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                break

        if not key:
            return None, "Key not found"

        # Verify token (skip audience validation for mock token exchange)
        decoded = jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            options={"verify_exp": True, "verify_aud": False}
        )

        return decoded, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except Exception as e:
        return None, str(e)

@app.route('/api/resource', methods=['GET'])
def protected_resource():
    """Protected endpoint requiring DPoP-bound access token"""
    start_time = time.time()

    # Extract tokens
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        print(f"ERROR: Missing authorization header")
        return jsonify({"error": "Missing authorization"}), 401

    access_token = auth_header[7:]  # Remove "Bearer "
    dpop_proof = request.headers.get('DPoP')

    if not dpop_proof:
        print(f"ERROR: Missing DPoP proof")
        return jsonify({"error": "Missing DPoP proof"}), 401

    # Verify access token
    token_start = time.time()
    decoded_token, error = verify_access_token(access_token)
    token_verify_ms = (time.time() - token_start) * 1000

    if error:
        print(f"ERROR: Token verification failed: {error}")
        return jsonify({"error": f"Invalid token: {error}"}), 403

    # Verify DPoP proof
    dpop_start = time.time()
    dpop_valid, dpop_error, jti = verify_dpop_proof(
        dpop_proof,
        request.method,
        request.url,
        access_token
    )
    dpop_verify_ms = (time.time() - dpop_start) * 1000

    if not dpop_valid:
        print(f"ERROR: DPoP verification failed: {dpop_error}")
        return jsonify({"error": f"Invalid DPoP: {dpop_error}"}), 403

    # Check jti replay
    jti_start = time.time()
    if jti_cache.is_replayed(jti):
        print(f"ERROR: DPoP replay detected for jti: {jti}")
        return jsonify({"error": "DPoP replay detected"}), 403

    jti_cache.add(jti)
    jti_check_ms = (time.time() - jti_start) * 1000

    total_verify_ms = (time.time() - start_time) * 1000

    # Return success with metrics
    return jsonify({
        "data": "Success",
        "subject": decoded_token.get('sub'),
        "actor": decoded_token.get('act'),
        "server_verify_ms": total_verify_ms,
        "breakdown": {
            "token_verify_ms": token_verify_ms,
            "dpop_verify_ms": dpop_verify_ms,
            "jti_check_ms": jti_check_ms
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
