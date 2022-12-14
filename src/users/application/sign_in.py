from appcore.domain.response import Response
from appcore.interfaces.db_connection_manager import connect_bd, disconnect_bd
from appcore.domain.status import Status
from users.domain.user import AuthCredentials
from users.interfaces.user_repository import are_valid_credentials, find_user


def sign_in(form):
    if sign_in_form_is_valid(form):
        conn = connect_bd()
        auth_credentials = AuthCredentials(**form)
        auth_credentials.encrypt_user_credentials()
        if are_valid_credentials(conn, auth_credentials):
            _status, des, code =  Status.OK, "Successfully logged in user", 200
        else:
            _status, des, code =  Status.UNAUTHORIZED, "Wrong credentials", 401
        disconnect_bd(conn)
        return Response(_status, des, code)
    return Response(Status.BAD_REQUEST, "algo", 400)

def sign_in_form_is_valid(form):
    return True, dict()
