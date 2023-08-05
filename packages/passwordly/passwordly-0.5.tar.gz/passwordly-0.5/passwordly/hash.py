import bcrypt

def createHash(password):
  salt = bcrypt.gensalt(11)
  return bcrypt.hashpw(password, salt)

def checkHash(password, hash):
  result = bcrypt.hashpw(password, hash)
  return (result == hash)

