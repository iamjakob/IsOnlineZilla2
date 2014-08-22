IsOnlineZilla
==============

you can see how it runs at:
  http://androidadvance.com:1337/
  
  


a free service, written in Python Flask + Tornado + a simple google appegine app
to notify if your website is offline.

How to install it:

1. a server with python flask installed

sudo apt-get install -y build-essential python python-dev python-pip python-mysqldb libmysqlclient-dev supervisor libmemcached-dev memcached python-memcache
pip install flask flask-login flask-mail sqlalchemy flask-sqlalchemy flask-wtf flask-migrate tornado flask-cache simpleencode tornado
pip install pdfminer

2. Copy paste it. "python run.py"
   Do you see it in the browser ?
   
   
3. Install supervisor and let it run indefinetly

4. Setup a google appegine app that you use just to send emails.

5. Create a cronjob every 5 (? less, more ?) minutes that runs ping_deamon.py [TODO: recode it]

