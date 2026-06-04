from website.database.User import User as DBUser
'''

User class handles user authentication and sessions using Flask-Login
Use the get_user static method to retreive a user but user_id

'''

class User:
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password

        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return self.user_id
    
    @staticmethod
    def get_user(user_id):
        user = DBUser.query.filter_by(id=user_id).first()
        if user:
            return User(user.id, user.username, user.password)
        return None
