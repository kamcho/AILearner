from django.db import models

# Create your models here.
import uuid

from django.db import models
from datetime import datetime,timedelta

from django.urls import reverse
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)



class MyUserManager(BaseUserManager):
    def create_user(self,email,role, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """

        user = self.model(


            email=email,
            role=role,



        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, role, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(

            email=email,
            role=role,

            password=password,

        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    class Role(models.TextChoices):
        Student="Student"
        Teacher="Teacher"
        ADMIN="ADMINISTRATOR"
    base_role=Role.ADMIN

    email = models.EmailField(unique=True)
    role=models.CharField(max_length=15,choices=Role.choices,default=Role.ADMIN)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)


    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    # required_field_name=['role']


    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


# EMPLOYER MANAGER
class TeacherManager(BaseUserManager):
    def get_queryset(self,*args,**kwargs):
        result=super().get_queryset(*args,**kwargs)
        return result.filter(role=MyUser.Role.Teacher)
class Teacher(MyUser):
    base_role = MyUser.Role.Teacher
    teacher=TeacherManager()
    class Meta:
        proxy=True

# EXPERT MANAGER
class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=MyUser.Role.Student)

class Student(MyUser):
    base_role = MyUser.Role.Student
    #
    student = StudentManager()

    class Meta:
        proxy = True



class PersonalProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    f_name = models.CharField(max_length=30, default='F_NAME')
    l_name = models.CharField(max_length=30, default='M_NAME')
    surname = models.CharField(max_length=30, default='SURNAME',blank=True)
    gender = models.CharField(max_length=10,default="FEMALE",blank=True)
    pic = models.ImageField(upload_to='profile_pics/', default='E:\\IPweb\\media\\profile_pics\\TT.png')
    phone1=models.CharField(max_length=15)
    phone2=models.CharField(max_length=15)


    def __str__(self):
        return self.user.email

class AcademicProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    school = models.CharField(max_length=100)
    county = models.CharField(max_length=20)

    def __str__(self):
        return self.user.email





