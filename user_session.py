# user_session.py
class UserSession:
    _instance = None
    _user_data = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = UserSession()
        return cls._instance

    def set_user(self, user_data):
        UserSession._user_data = user_data

    def get_user(self):
        return UserSession._user_data

    def clear_user(self):
        UserSession._user_data = None