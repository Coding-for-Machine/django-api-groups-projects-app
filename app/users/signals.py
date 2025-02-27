from django.db.models.signals import post_save
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Profile, MyUser
from django.contrib.auth.models import Group, Permission


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    groups = ["Student", "Teacher", "Staff", "Superuser"]
    
    for group_name in groups:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"Guruh yaratildi: {group_name}")

    staff_group, _ = Group.objects.get_or_create(name="Staff")
    permissions = Permission.objects.filter(content_type__app_label="admin")
    staff_group.permissions.set(permissions)

    superuser_group, _ = Group.objects.get_or_create(name="Superuser")
    all_permissions = Permission.objects.all()
    superuser_group.permissions.set(all_permissions)
    

@receiver(post_save, sender=MyUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Profil yaratish
        Profile.objects.create(
            user=instance,
            first_name=instance.first_name or '',
            last_name=instance.last_name or ''
        )
    else:
        # Profilni yangilash
        profile, _ = Profile.objects.get_or_create(user=instance)
        profile.first_name = instance.first_name
        profile.last_name = instance.last_name
        profile.save()

            
@receiver(post_save, sender=MyUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()