import os
from .auth import generate_test_token

class JWTAuthMixin:
    """
    Mixin to add JWT authentication to test cases.
    """
    
    def setUp(self):
        """
        Set up JWT authentication for test cases.
        """
        super().setUp()
        
        # Check if JWT keys are set in environment variables
        if not os.environ.get('JWT_PRIVATE_KEY') or not os.environ.get('JWT_PUBLIC_KEY'):
            self.skipTest("JWT_PRIVATE_KEY and JWT_PUBLIC_KEY environment variables must be set for this test")
        
        # Generate a token
        self.token = generate_test_token()
        
        # Set the Authorization header for all requests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
    
    def remove_auth(self):
        """
        Remove authentication credentials.
        """
        self.client.credentials()
    
    def set_auth(self, roles=None):
        """
        Set authentication credentials with specific roles.
        
        Args:
            roles (list): List of roles to include in the token.
        """
        token = generate_test_token(roles=roles)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")