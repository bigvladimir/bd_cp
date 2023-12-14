from .env import db_hid_params

db_params = {
    'host': 'localhost',
    'dbname': 'hotel',
    'admin': db_hid_params['admin'],
    'visitor': db_hid_params['visitor'],
    'visitor_pass': db_hid_params['visitor_pass']
}
