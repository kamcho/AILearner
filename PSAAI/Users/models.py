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
    def create_user(self,email,role,uuid=uuid ,password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """

        user = self.model(


            email=email,
            role=role,
            uuid=uuid



        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, role, uuid, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(

            email=email,
            role=role,
            uuid=uuid,
            password=password,

        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    class Role(models.TextChoices):
        Student = "Student"
        Teacher = "Teacher"
        ADMIN = "ADMINISTRATOR"
        Guardian = 'Guardian'
        Supervisor = "Supervisor"

    base_role = Role.Student
    email = models.EmailField(unique=True)
    uuid = models.CharField(max_length=100, default=uuid.uuid4, editable=True)
    role = models.CharField(max_length=15, choices=Role.choices, default=base_role)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    objects = MyUserManager()
    USERNAME_FIELD = 'email'


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


class TeacherManager(BaseUserManager):
    def get_queryset(self,*args,**kwargs):
        result = super().get_queryset(*args,**kwargs)
        return result.filter(role=MyUser.Role.Teacher)


class Teacher(MyUser):
    base_role = MyUser.Role.Teacher
    teacher = TeacherManager()

    class Meta:
        proxy = True


class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=MyUser.Role.Student)


class Student(MyUser):
    base_role = MyUser.Role.Student
    student = StudentManager()

    class Meta:
        proxy = True


class GuardianManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=MyUser.Role.Guardian)


class Guardian(MyUser):
    base_role = MyUser.Role.Guardian
    guardian = GuardianManager()

    class Meta:
        proxy = True


class SupervisorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=MyUser.Role.Supervisor)


class Supervisor(MyUser):
    base_role = MyUser.Role.Supervisor
    student = SupervisorManager()

    class Meta:
        proxy = True


class PersonalProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    f_name = models.CharField(max_length=30, default='F_NAME')
    ref_id = models.CharField(max_length=100, blank=True)
    l_name = models.CharField(max_length=30, default='M_NAME')
    surname = models.CharField(max_length=30, default='SURNAME',blank=True)
    gender = models.CharField(max_length=10,default="FEMALE",blank=True)
    pic = models.ImageField(upload_to='profile_pics/', default='E:\\IPweb\\media\\profile_pics\\TT.png')
    phone1=models.CharField(max_length=15)
    phone2=models.CharField(max_length=15)
    country = models.CharField(max_length=10,default="Kenya",blank=True)
    city = models.CharField(max_length=10,default="Nairobi",blank=True)
    area = models.CharField(max_length=10,default="Karen",blank=True)



    def __str__(self):
        return self.user.email

class AcademicProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    school = models.CharField(max_length=100)
    county = models.CharField(max_length=20)
    grade = models.IntegerField(default=1)

    def __str__(self):
        return self.user.email





