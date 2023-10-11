from django.shortcuts import render
# from django.contrib.auth import get_user_model

# User = get_user_model()

# user = User.objects.create_user(username='user1', email='user1@example.com', password='password')
# analyst = User.objects.create_user(username='analyst1', email='analyst1@example.com', password='password', role='analyst')
# admin = User.objects.create_superuser(username='admin1', email='admin1@example.com', password='password', role='admin')

def is_admin(user):
    return user.role == 'admin'

def is_analyst(user):
    return user.role == 'analyst'