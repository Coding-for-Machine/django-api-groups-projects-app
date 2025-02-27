from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, FileExtensionValidator


class MyUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email maydoni talab qilinadi!")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True) 
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user



    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun `is_staff=True` bo‘lishi shart!")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun `is_superuser=True` bo‘lishi shart!")

        return self.create_user(email, password, **extra_fields)



ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("staff", "Staff"),
        ("superuser", "Superuser"),
    ]
# ustom User Model
class MyUser(AbstractBaseUser, PermissionsMixin):
    # username = None
    email = models.EmailField(max_length=250, unique=True, verbose_name="Email manzil")
    first_name = models.CharField(max_length=30, blank=True, null=True, verbose_name="Ism")
    last_name = models.CharField(max_length=30, blank=True, null=True, verbose_name="Familiya")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_staff = models.BooleanField(default=False, verbose_name="Xodim")
    is_deleted = models.BooleanField(default=False, verbose_name="O‘chirilgan")  # Soft delete
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")
    primary_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="primary_users")
    supplementary_groups = models.ManyToManyField(Group, blank=True, related_name="extra_users")
    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def delete(self, *args, **kwargs):
        """Soft Delete: Foydalanuvchini o‘chirib tashlamasdan yashirin qiladi"""
        self.is_deleted = True
        self.save()

    def restore(self):
        """Foydalanuvchini tiklash"""
        self.is_deleted = False
        self.save()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        is_new = self.id is None 

        super().save(*args, **kwargs)

        # Guruhni aniqlash va qo‘shish
        group, _ = Group.objects.get_or_create(name=self.role.capitalize())
        self.primary_group = group
        self.groups.set([group])  # Faqat bitta primary guruhni o‘rnatish

        # Staff bo‘lsa, unga maxsus ruxsatlar beriladi
        if self.is_staff:
            staff_group, _ = Group.objects.get_or_create(name="Staff")
            self.supplementary_groups.add(staff_group)
            self.groups.add(staff_group)

        # Superuser bo‘lsa, barcha huquqlarga ega bo‘lsin
        if self.is_superuser:
            all_groups = Group.objects.all()
            self.supplementary_groups.set(all_groups)
            self.groups.set(all_groups)

        super().save(*args, **kwargs)

LANGUAGE_LEVEL_CHOICES = [
        ('A1', 'Beginner'),
        ('A2', 'Elementary'),
        ('B1', 'Intermediate'),
        ('B2', 'Upper-Intermediate'),
        ('C1', 'Advanced'),
        ('C2', 'Proficient'),
]
# C
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 primary_key=True, 
                                 verbose_name="Foydalanuvchi", 
                                 )
    #  user = User.objects.get(id=1)
    #  user.profile.all()
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ism")
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Familiya")
    image = models.ImageField(upload_to='profile/', default='user/user.png', blank=True, 
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], verbose_name="Profil rasmi")
    bio = models.TextField(blank=True, null=True, verbose_name="Bio")
    age = models.IntegerField(default=12, validators=[MinValueValidator(12)], verbose_name="Yosh")
    language_level = models.CharField(max_length=3, choices=LANGUAGE_LEVEL_CHOICES, default="A1")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.email})"

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profillar"
        ordering = ['-created_at']

