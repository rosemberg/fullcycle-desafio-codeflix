# fullcycle-desafio-codeflix

## JWT Authentication for Tests

### Setup

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Generate RSA keys for JWT signing and verification:

```bash
python -m desafio_codeflix.generate_keys
```

This will create a `.env` file with the RSA keys as environment variables.

3. Load the environment variables before running tests:

```bash
export $(grep -v '^#' .env | xargs)
```

### Running Tests

To run all tests in the project, you can use the standard Django test command:

```bash
python manage.py test
```

You can also run specific test classes:

```bash
python manage.py test desafio_codeflix.tests.CastMemberModelTest
python manage.py test desafio_codeflix.tests.VideoWithoutMediaEndToEndTest
python manage.py test desafio_codeflix.tests.JWTAuthTest
```

### Using JWT Authentication in Tests

To use JWT authentication in your tests, you can use the `JWTAuthMixin` class:

```python
from rest_framework.test import APITestCase
from desafio_codeflix.test_utils import JWTAuthMixin

class MyTestCase(JWTAuthMixin, APITestCase):
    def test_authenticated_request(self):
        # The JWTAuthMixin.setUp method has already set the Authorization header
        # with a JWT token that has the default roles.
        response = self.client.get('/api/some-endpoint/')
        self.assertEqual(response.status_code, 200)

        # Test with different roles
        self.set_auth(roles=["user"])
        response = self.client.get('/api/some-endpoint/')
        self.assertEqual(response.status_code, 200)

        # Test without authentication
        self.remove_auth()
        response = self.client.get('/api/some-endpoint/')
        # If the endpoint requires authentication, this would return 401 Unauthorized
```

### JWT Token Format

The generated JWT tokens have the following payload format, which matches Keycloak's format:

```json
{
    "exp": "expiration-time",
    "iat": "issued-at-time",
    "jti": "test-token-id",
    "iss": "test-issuer",
    "sub": "test-subject",
    "typ": "Bearer",
    "realm_access": {
        "roles": [
            "offline_access",
            "admin",
            "uma_authorization",
            "default-roles-codeflix"
        ]
    }
}
```

### Generating Tokens Manually

You can also generate tokens manually using the `generate_test_token` function:

```python
from desafio_codeflix.auth import generate_test_token

# Generate a token with default roles
token = generate_test_token()

# Generate a token with specific roles
token = generate_test_token(roles=["user", "admin"])

# Generate a token with a specific expiration time (in minutes)
token = generate_test_token(expiration_minutes=30)
```

### Decoding Tokens

You can decode tokens using the `decode_token` function:

```python
from desafio_codeflix.auth import decode_token

decoded = decode_token(token)
print(decoded)
```
