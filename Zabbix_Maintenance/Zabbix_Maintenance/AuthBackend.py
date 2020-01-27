class ZabbixBackend:

    def authenticate(self, request, username=None, password=None):
        from app.static.app.python_scripts.zabbix import Zabbix         # import zabbix module
        from django.contrib.auth.hashers import check_password
        from django.contrib.auth.models import User
        from app.models import Person                                   # to use models in backend
        if Zabbix.validate_auth(username, password):                    # use static method which try logging in and return boolean    
            try:
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                # no need save person because when save user person saved too
            except User.DoesNotExist:
                # Create a new user.
                user = User(username=username, password=password)
                #user.is_staff = True
                #user.is_superuser = True           # uncomment if u need django admin acces to all users
                user.save()                         # first save user, and after change person                         
                person = user.person
                person.login = username
                person.save()
            return user
        else:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    if user.is_superuser and user.is_staff:
                        return user                 # if cant log in into zabbix but it superuser
            except:
                return None
        return None

    def get_user(self, user_id):
        from django.contrib.auth.models import User
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
