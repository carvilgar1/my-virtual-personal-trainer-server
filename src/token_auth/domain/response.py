from src.common.domain import Response


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
