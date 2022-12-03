def find_user(connection, **kwargs):
    return connection.get_database('my_virtual_personal_trainer').get_collection('user').find_one(kwargs)

def insert_user(connection, **kwargs):
    return connection.get_database('my_virtual_personal_trainer').get_collection('user').insert_one(kwargs)

def is_email_already_register(connection, email):
    return connection.get_database('my_virtual_personal_trainer').get_collection('user').count_documents({'auth_credentials.email': email}) > 0

def are_valid_credentials(connection, auth_credentials):
    return connection.get_database('my_virtual_personal_trainer').get_collection('user').count_documents({'auth_credentials.email': auth_credentials.email, 'auth_credentials.password': auth_credentials.password}) > 0