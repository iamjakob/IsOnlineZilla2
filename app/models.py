# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import and_

from app import *


ROLE_USER = 0
ROLE_ADMIN = 1
secret_key = "3l4dsjfalkjf30ij43jkLM"


class TheModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100))
    website = db.Column(db.String(100))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    found_online_date = db.Column(db.DateTime)
    found_offline_date = db.Column(db.DateTime)
    is_offline = db.Column(db.SmallInteger, default=0)
    enable_notifications = db.Column(db.SmallInteger, default=1)
    notifications_limit = db.Column(db.Integer, default=200)
    is_deleted = db.Column(db.SmallInteger, default=0)


    def validate_new_themodel(self, user_email, website):

        is_in_the_db = db.session.query(TheModel.created_date).filter(and_(TheModel.user_email == user_email, TheModel.website == website)).count()
        # ------ check is in the db ---------
        if is_in_the_db == 0:
            return "ok"
        else:
            return "already in the database"


    def add_new_themodel(self, user_email, website, user_ip):


        print "trying to add: " + user_email

        validation_message = self.validate_new_themodel(user_email, website)

        if validation_message == "ok":
            new_user = TheModel(user_email=user_email, website=website, is_offline=2, enable_notifications=1, is_deleted=0)
            db.session.add(new_user)
            db.session.commit()
            return "ok"
        else:
            return validation_message

    def __repr__(self):
        return '<TheModel %r %r>' % (self.id, self.user_email)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100))
    user_ip = db.Column(db.String(40))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    role = db.Column(db.SmallInteger, default=ROLE_USER)


    @staticmethod
    def get(userid):
        usr = Users.query.get(int(userid))
        return usr

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def clear_table(self):

        number_deleted = Users.query.delete()
        db.session.commit()

        return number_deleted


    def check_user_and_password(self, muser_email):


        mUser = db.session.query(Users).filter(Users.user_email == muser_email).first()

        if mUser == None:
            return "user inexistent"
        else:
            return "ok"


    def validate_new_user(self, user_email, user_ip):

        is_in_the_db = db.session.query(Users.created_date).filter(Users.user_email == user_email).count()
        # ------ check is in the db ---------
        if is_in_the_db == 0:
            return "ok"
        else:
            return "already in the database"


    def add_new_user(self, user_email, user_ip):


        print "adding: " + user_email

        validation_message = self.validate_new_user(user_email, user_ip)
        if validation_message == "ok":
            new_user = Users(user_email=user_email, user_ip=user_ip)
            db.session.add(new_user)
            db.session.commit()
            return "ok"
        else:
            return validation_message


    def __repr__(self):
        return '<User %r %r>' % (self.id, self.user_email)