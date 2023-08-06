from webapp.users import User
  
  
DBTYPE = 'oracle'
DBHOST = 'fasolt.stanford.edu:1521'
DBNAME = 'SDEV'
SCHEMA = 'bud'
                           
HOST = '0.0.0.0'
PORT = 5000
SECRET_KEY = "enter your secret key here"
    
usernames = {'maria', 'julie', 'kpaskov', 'dwight', 'fisk', 'rama', 'stacia', 'nash', 'marek', 'otto'}
keys = range(0, len(usernames))
values = map(lambda (i, username): User(username, i), enumerate(usernames))

USERS = dict(zip(keys, values))
USERS[len(usernames)+1] = User('guest', len(usernames)+1, False)

USER_NAMES = dict((u.name, u) for u in USERS.itervalues())
