from datetime import datetime

from src.common.domain import Response


class TokenPayload:
    def __init__(self, sub: str, username: str, email: str):
        self.sub = sub
        self.username = username
        self.email = email

    def set_expiration(self, expiration: int):
        self.iat = datetime.now().timestamp()
        self.exp = self.iat + expiration

    def to_dict(self):
        return {
            'sub': self.sub,
            'username': self.username,
            'email': self.email,
            'iat': int(self.iat),
            'exp': int(self.exp)
        }


class JwtTokenResponse(Response):
    def __init__(self, access_token: str, refresh_token: str, expires_in: int, token_type: str = 'Bearer'):
        super().__init__(status=None)
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.token_type = token_type

    def to_json(self):
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_in': self.expires_in,
            'token_type': self.token_type
        }
