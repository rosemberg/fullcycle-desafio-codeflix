import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def generate_rsa_keys():
    """
    Generate RSA key pair for JWT token signing and verification.
    
    Returns:
        tuple: (private_key_pem, public_key_pem) as strings
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Get private key in PEM format
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    # Get public key in PEM format
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_key_pem, public_key_pem

def save_keys_to_env_file():
    """
    Generate RSA keys and save them to a .env file.
    """
    private_key, public_key = generate_rsa_keys()
    
    with open('.env', 'a') as f:
        f.write(f'JWT_PRIVATE_KEY="""{private_key}"""\n')
        f.write(f'JWT_PUBLIC_KEY="""{public_key}"""\n')
    
    print("RSA keys generated and saved to .env file.")
    print("Make sure to load these environment variables before running tests.")

if __name__ == "__main__":
    save_keys_to_env_file()