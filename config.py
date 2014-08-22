# -*- coding: utf-8 -*-

import os

basedir = os.path.abspath(os.path.dirname(__file__))



SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


CSRF_ENABLED = True
secret_key = "3l4dsfalkjf30ij43jkLMx"

NUMBER_OF_POSITIVES = 5
#UPLOAD_FOLDER = '/home/pravopomosht/app/static/uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])


