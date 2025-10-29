import json
import hashlib
import time
from jwcrypto import jwk, jwt

def verify_dpop_proof(dpop_proof, http_method, http_uri, access_token):
    """
    Verify DPoP proof according to RFC 9449
    Returns: (is_valid, error_message, jti)
    """
    try:
        # Decode DPoP JWT header without verification
        token = jwt.JWT()
        token.deserialize(dpop_proof)

        # Get header and claims (already parsed as dicts by jwcrypto)
        header_str = token.token.jose_header
        claims_str = token.token.objects['payload']

        header = json.loads(header_str) if isinstance(header_str, (str, bytes)) else header_str
        claims = json.loads(claims_str) if isinstance(claims_str, (str, bytes)) else claims_str

        # Verify header
        if header.get('typ') != 'dpop+jwt':
            return False, "Invalid typ", None

        if header.get('alg') != 'ES256':
            return False, "Invalid alg", None

        if 'jwk' not in header:
            return False, "Missing jwk", None

        # Extract public key from header
        public_key = jwk.JWK(**header['jwk'])

        # Verify signature using the JWT token's make_signed_token verification
        # The token is already deserialized, we verify by trying to deserialize again with key
        verified_token = jwt.JWT(jwt=dpop_proof, key=public_key)

        # Verify claims
        jti = claims.get('jti')
        htm = claims.get('htm')
        htu = claims.get('htu')
        iat = claims.get('iat')
        ath = claims.get('ath')

        if not all([jti, htm, htu, iat, ath]):
            return False, "Missing required claims", None

        # Verify htm (HTTP method)
        if htm != http_method:
            return False, f"htm mismatch: {htm} != {http_method}", None

        # Verify htu (HTTP URI) - normalize by removing query/fragment
        normalized_uri = http_uri.split('?')[0].split('#')[0]
        normalized_htu = htu.split('?')[0].split('#')[0]

        if normalized_htu != normalized_uri:
            return False, f"htu mismatch", None

        # Verify iat (issued at time - not too old)
        current_time = int(time.time())
        if abs(current_time - iat) > 60:  # 60 second window
            return False, "iat too old or future", None

        # Verify ath (access token hash)
        computed_ath = hashlib.sha256(access_token.encode('utf-8')).hexdigest()
        if ath != computed_ath:
            return False, "ath mismatch", None

        return True, None, jti

    except Exception as e:
        return False, str(e), None
