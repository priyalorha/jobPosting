import os
from datetime import datetime

from mongoengine import *

connect(db='test',
        username=os.getenv('username'),
        password=os.getenv('password'),
        host=os.getenv('MONGODB_URL'))


class Users(Document):
    name = StringField()
    email = StringField(unique=True,
                        )
    mobile = StringField()
    photo = StringField()
    admin = BooleanField(
        default=False)

    meta = {
        'strict': False,
        'collect': 'jobuser'}

    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'mobile': self.mobile,
            'photo': self.photo,
            'admin': self.admin

        }


class jobPosting(Document):
    sequence = StringField()
    title = StringField()
    description = StringField()
    location = PointField()
    expiryDate = DateTimeField()
    whoApplied = ListField()

    meta = {
        'strict': False,
        'collection': 'jobposting',
        'indexes': ['location']
    }

    def to_dict(self):
        return {
            'sequence': self.id,
            'title': self.title,
            'description': self.description,
            'locality': self.location['coordinates'],
            'expiryDate': str(self.expiryDate),
            'whoApplied': self.whoApplied}


class cv(Document):
    id = StringField()
    name = StringField()

    meta = {
        'strict': False,
        'collect': 'cv'}

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,

        }

#
# print(jobPosting(title='software developer',
#                  description='testing aws code',
#
#                  expiryDate = datetime(month=12,year=2021,day=1)))
