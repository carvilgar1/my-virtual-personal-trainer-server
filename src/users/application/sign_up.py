from appcore.interfaces.db_connection_manager import connect_bd, disconnect_bd
from appcore.domain.status import Status
from appcore.domain.response import Response
from users.domain.user import User
from users.interfaces.user_repository import insert_user, is_email_already_register


def sign_up(form):
    if sign_up_form_is_valid(form):
        user = User(**form)
        user.auth_credentials.encrypt_user_credentials()
        conn = connect_bd()
        if is_email_already_register(conn, user.auth_credentials.email): 
            _status, des, code = Status.FORBIDDEN, "User already register", 403
        else:
            insert_user(conn, **user.to_json())
            _status, des, code = Status.OK, "User has been registered satisfactorily", 201
        disconnect_bd(conn)
        return Response(_status, des, code)
    return Response(Status.BAD_REQUEST, "algo", 400)

def sign_up_form_is_valid(form):
    return True, dict()