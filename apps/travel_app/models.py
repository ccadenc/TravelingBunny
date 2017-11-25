from __future__ import unicode_literals

from django.db import models
import bcrypt
import datetime
from django.forms.fields import DateTimeField
# Create your models here.


class UserManager(models.Manager):
    def validate_reg(self, postData):
        errors = []
        name = postData['name']
        if len(name) <= 2 or not name.isalpha():
            errors.append(
                "Name must be more than 2 characters and letters only")
        if len(postData['alias']) <= 2:
            errors.append("Username must be more than 2 characters")

        if len(postData['password']) < 8:
            errors.append("Password must be at least 8 characters long")
        if postData['password'] != postData['confirm_pass']:
            errors.append("confirmation password did not match")
        if len(User.objects.filter(alias=postData['alias'])) > 0:
            errors.append("This alias is already in use.")
        if len(errors) > 0:
            return {
                'success': False,
                'errors': errors
            }
        else:
            pw_hash = bcrypt.hashpw(
                postData['password'].encode(), bcrypt.gensalt())
            user = User.objects.create(
                name=postData['name'], alias=postData['alias'], password=pw_hash)
            return {
                'success': True,
                'user': user
            }

    def validate_login(self, postData):
        errors = []
        if len(postData['username']) == 0:
            errors.append("Please provide username")
        if len(postData['password']) == 0:
            errors.append("Please provide your password")
        if len(User.objects.filter(alias=postData['username'])) == 0:
            errors.append("email could not be found")
        if not bcrypt.checkpw(postData['password'].encode(), User.objects.get(alias=postData['username']).password.encode()):
            errors.append("invalid password")
        if len(errors) > 0:
            return {
                'success': False,
                'errors': errors
            }
        else:
            return {
                'success': True,
                'user': User.objects.get(alias=postData['username'])
            }


class User(models.Model):
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)

    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def __str__(self):
        return self.name

# this is for add a trip


class TravelManager (models.Manager):
    def validate_create(self, postData, user_id):
        errors = []
        timeGood = False
        print postData
        now = datetime.datetime.now()
        if 'travel_from' in postData:
            try:
                from_time = datetime.datetime.strptime(
                    postData['travel_from'], '%Y-%m-%d')
                print from_time
                if 'travel_till' in postData:
                    try:
                        to_time = datetime.datetime.strptime(
                            postData['travel_till'], '%Y-%m-%d')
                        timeGood = True
                    except:
                        errors.append("To date was incorrectly provided")
            except:
                errors.append("From date was incorrectly provided")

        # if 'travel_till' in postData:
        #to_time = DateTimeField().clean(postData['travel_till'])

        if len(postData['destination']) <= 2:
            errors.append("destination was too short")
        if len(postData['description']) <= 2:
            errors.append("description was too short")
        if len(postData['travel_from']) < 1:
            errors.append("from travel date was not provided")
        if len(postData['travel_till']) < 1:
            errors.append("to travel date was not provided")

        # if len(postData['travel_from']) < 1 and len(postData['travel_till']) < 1:
        if timeGood:
            if from_time.date() < now.date():
                errors.append("cannot schedule into the past")
                print from_time
                print now.date()
            if from_time.date() > to_time.date():
                errors.append(
                    "cannot schedule return date before leaving date")
        if len(errors) > 0:
            return {
                'success': False,
                'errors': errors
            }
        else:
            user = User.objects.get(id=user_id)
            travel = Travel.objects.create(
                destination=postData['destination'], description=postData['description'],
                date_from=postData['travel_from'], date_to=postData['travel_till'], creator=user)
            return {
                'success': True,
                'travel': travel
            }


class Travel(models.Model):
    destination = models.CharField(max_length=225)
    description = models.CharField(max_length=255)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    creator = models.ForeignKey(User, related_name="travel_created")
    join_users = models.ManyToManyField(User, related_name="travel_join")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TravelManager()

    def __str__(self):
        return self.destination + ' ' + self.description
