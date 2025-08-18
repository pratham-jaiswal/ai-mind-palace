from clerk_backend_api import Clerk
from services.user_service import UserService
from jose import jwt
import os

def get_user_data(jwt_bearer: str = None):
    with Clerk(bearer_auth=os.getenv('CLERK_SECRET_KEY')) as clerk:
            jwks = clerk.jwks.get_jwks()

            assert jwks is not None

            header = jwt.get_unverified_header(jwt_bearer)

            key = next((k for k in jwks.keys if k.kid == header["kid"]), None)
            if not key:
                raise Exception("Public key not found in Clerk JWKS")

            decoded_jwt = jwt.decode(
                jwt_bearer,
                key.model_dump(),
                algorithms=[header["alg"]],
            )
            clerk_id = decoded_jwt["user_id"]
            user = UserService.get_by_clerk_id(clerk_id)
            user_id = user.id if user else None

            return {
                "user_id": user_id,
                "clerk_id": clerk_id
            }