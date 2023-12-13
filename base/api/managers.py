from django.contrib.auth.models import BaseUserManager

class CustomManagers(BaseUserManager):
    def _create_user(self, phonenumber, username, password=None, **extrafileds):
        if not phonenumber:
            raise ValueError("the give phonenumber must be set")
        phonenumber = phonenumber
        user = self.model(
            phonenumber = phonenumber,
            username = username,
            **extrafileds
        )
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_user(self, phonenumber, username, password=None, **extrafileds):
        extrafileds.setdefault("is_superuser", False)
        extrafileds.setdefault("is_staff", False)
        return self._create_user(phonenumber, username, password, **extrafileds)
    
    def create_superuser(self, phonenumber, username, password, **extrafileds):
        extrafileds.setdefault("is_superuser", True)
        extrafileds.setdefault("is_staff", True)

        if extrafileds.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superus=True")
        if extrafileds.get("is_staff") is not True:
            raise ValueError("Superuser must have is is_staff=True")
        
        return self._create_user(phonenumber, username, password, **extrafileds)