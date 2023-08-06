from mongokit import Document, Connection


class User(Document):
  ''' Example class for tests
  '''
  __collection__ = 'users'
  __database__ = 'test'

  structure = { 'name': basestring, 'email': basestring, 'age': int, 'admin': bool }


if __name__ == "__main__":
  connection = Connection()
  connection.register([User])

  myklass = User

  user = connection.myklass()

  print user

