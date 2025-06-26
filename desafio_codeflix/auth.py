import os
import jwt
from datetime import datetime, timedelta

def generate_test_token(roles=None, expiration_minutes=60):
    """
    Generate a JWT token for testing purposes with the same format as Keycloak.
    
    Args:
        roles (list): List of roles to include in the token. Defaults to a standard set if None.
        expiration_minutes (int): Token expiration time in minutes. Defaults to 60 minutes.
        
    Returns:
        str: JWT token
    
    Raises:
        ValueError: If the private key is not set in the environment variables.
    """
    if roles is None:
        roles = ["offline_access", "admin", "uma_authorization", "default-roles-codeflix"]
    
    # Get the private key from environment variable
    private_key = os.environ.get('JWT_PRIVATE_KEY')
    if not private_key:
        raise ValueError("JWT_PRIVATE_KEY environment variable is not set")
    
    # Convert the private key string to bytes
    private_key_bytes = private_key.encode('utf-8')
    
    # Current time and expiration time
    now = datetime.utcnow()
    expiration = now + timedelta(minutes=expiration_minutes)
    
    # Create the payload with the same format as Keycloak
    payload = {
        "exp": expiration,
        "iat": now,
        "jti": "test-token-id",
        "iss": "test-issuer",
        "sub": "test-subject",
        "typ": "Bearer",
        "realm_access": {
            "roles": roles
        }
    }
    
    # Encode the token
    token = jwt.encode(payload, private_key_bytes, algorithm="RS256")
    
    return token

def decode_token(token):
    """
    Decode a JWT token.
    
    Args:
        token (str): JWT token to decode
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        ValueError: If the public key is not set in the environment variables.
    """
    # Get the public key from environment variable
    public_key = os.environ.get('JWT_PUBLIC_KEY')
    if not public_key:
        raise ValueError("JWT_PUBLIC_KEY environment variable is not set")
    
    # Convert the public key string to bytes
    public_key_bytes = public_key.encode('utf-8')
    
    # Decode the token
    decoded = jwt.decode(token, public_key_bytes, algorithms=["RS256"])
    
    return decoded