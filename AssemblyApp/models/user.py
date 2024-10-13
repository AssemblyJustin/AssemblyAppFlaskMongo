from flask_login import UserMixin
from app import login_manager, mongo
from bson import ObjectId

@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user:
        return User(user)
    return None

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data.get('username', '')
        self.email = user_data.get('email', '')
        self.assigned_projects = user_data.get('assigned_projects', [])
        self.role = user_data.get('role', 'engineer')

    def is_admin(self):
        return self.role == 'admin'