import envy
import redshift_connector as red

def __init__(host, port, user, password, database):
    global profile
    profile = {'host': host, 'port': port, 'user': user, 'password': password, "database": database}
    pass

def connect(path=None):
    global profile
    if path is not None:
        profile = envy.arbiter(path, default=envy.is_json(path),flags=[envy.SNAKE_CASE])
    profile['port'] = int(profile['port'])
    conn = red.connect(**profile)
    del profile
    return conn