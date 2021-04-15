from abc import ABC


class Login(ABC):
    """ Abstract class that supports the varied type of login features available. """

    def check_login_page_title(self):
        pass

    def login(self, user_name: str, password: str):
        pass
