def find_user(connection, **kwargs):
    return connection.get_database('my_virtual_personal_trainer').get_collection('user').find_one(kwargs)

def insert_user(connection, **kwargs):
    return connection.get_database('my_virtual_personal_trainer').get_collection('user').insert_one(kwargs)