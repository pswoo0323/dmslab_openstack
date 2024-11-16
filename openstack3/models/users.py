from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, userID, userEmail, password, userName, **extra_fields):
        if not userID or not userEmail:
            raise ValueError("userID와 userEmail은 필수입니다.")

        user = self.model(
            userID=userID,
            userEmail=userEmail,
            userName=userName,
            **extra_fields
        )
        user.set_password(password)  # 암호화된 비밀번호 설정
        user.save(using=self._db)
        return user

    def create_superuser(self, userID, userEmail, password, userName, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)  # 관리자 페이지 접근 허용
        extra_fields.setdefault('approve', True)
        return self.create_user(userID, userEmail, password, userName, **extra_fields)


class CustomUser(AbstractBaseUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    userID = models.CharField(max_length=100, unique=True)
    userEmail = models.EmailField(unique=True)
    userName = models.CharField(max_length=100)
    userDetail = models.TextField(blank=True, null=True)
    userRole = models.CharField(max_length=50, blank=True, null=True)
    userPriority = models.CharField(max_length=50, blank=True, null=True)
    approve = models.BooleanField(default=False)  # 승인 여부
    is_staff = models.BooleanField(default=False)  # 관리자 접근 여부
    is_superuser = models.BooleanField(default=False)  # 슈퍼유저 여부

    objects = CustomUserManager()

    USERNAME_FIELD = 'userID'
    REQUIRED_FIELDS = ['userEmail', 'userName']

    def __str__(self):
        return self.userID
