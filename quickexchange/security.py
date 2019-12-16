from quickexchange import bcrypt
from quickexchange.models import User

# Function will be used to authenticate a user
def authenticate(email, password):
  user = User.query.filter_by(email=email).first()
  if user and bcrypt.check_password_hash(user.password, password):
    return user


def identity(payload):
  user_id = payload['identity']
  print(f"Target id: {user_id}")
  return User.query.filter_by(id=user_id).first()
