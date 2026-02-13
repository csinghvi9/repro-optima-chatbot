import jwt
from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

PUBLIC_ENDPOINTS = [
    "/",
    "/api/admin_auth/login",
    "/api/admin_auth/signup",
    "/api/auth/guest_token",
    "/docs",
    "/openapi.json",
]


class TrimmedAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        guest_secret_key: str,
        admin_secret_key: str,
        refresh_secret_key: str,
        algorithm: str,
    ):
        super().__init__(app)
        self.guest_secret_key = guest_secret_key
        self.admin_secret_key = admin_secret_key
        self.refresh_secret_key = refresh_secret_key
        self.algorithm = algorithm

    @staticmethod
    def extract_token(authorization: str) -> str:
        if authorization and authorization.startswith("Bearer "):
            return authorization.split(" ")[1]
        return None

    async def dispatch(self, request: Request, call_next):

        if request.url.path in PUBLIC_ENDPOINTS:
            response = await call_next(request)
            return response
        if request.method == "OPTIONS":
            return await call_next(request)

        authorization: str = request.headers.get("Authorization")

        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        try:
            token = TrimmedAuthMiddleware.extract_token(authorization)

            if token:
                pass
            else:
                raise HTTPException(status_code=401, detail="Invalid or missing token.")

            try:
                payload = jwt.decode(
                    token, self.guest_secret_key, algorithms=[self.algorithm]
                )
            except jwt.InvalidTokenError:
                try:
                    payload = jwt.decode(
                        token, self.admin_secret_key, algorithms=[self.algorithm]
                    )
                except jwt.InvalidTokenError:
                    try:
                        payload = jwt.decode(
                            token, self.refresh_secret_key, algorithms=[self.algorithm]
                        )
                    except jwt.InvalidTokenError:
                        raise HTTPException(status_code=401, detail="Invalid token")
            user_id = payload.get("user_id")

            if user_id is None:
                raise HTTPException(
                    status_code=401, detail="Token is invalid or expired"
                )

            request.state.user_id = user_id

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail="Token is invalid")
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid token: " + str(e))

        response = await call_next(request)
        return response
