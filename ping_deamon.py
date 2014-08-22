# -*- coding: utf-8 -*-

import datetime
import os
import threading
import time
import logging

import requests
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
)
db = SQLAlchemy(app)


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


def time_difference(now, then):
    now = int(time.time())  # epoch seconds
    then = now - 90000  # some time in the past
    d = divmod(now - then, 86400)  # days
    h = divmod(d[1], 3600)  # hours
    m = divmod(h[1], 60)  # minutes
    s = m[1]  # seconds

    return '%d hours, %d minutes, %d seconds' % (h[0], m[0], s)


def url_ok(url):
    try:
        r = requests.head("http://" + url)
        return r.status_code == 200
    except Exception, e:
        return False


def send_notification_email(to_email, subject, body):
    url_to_send = "http://isonlinezilla.appspot.com/sendemail?toemail=" + to_email + "&message=" + body + "&subject=" + subject
    try:
        response = requests.get(url_to_send)
        if response.content == "ok":
            print "send notification email to " + to_email
        else:
            print "notification email failed! " + str(response.content)
    except Exception, e:
        print "exception in sending email..."


class Pinger(object):
    status = {'alive': [], 'dead': []}  # Populated while we are running
    hosts = []  # List of all hosts/ips in our input queue

    # How many ping process at the time.
    thread_count = 4

    # Lock object to keep track the threads in loops, where it can potentially be race conditions.
    lock = threading.Lock()


    def pop_queue(self):
        ip = None

        self.lock.acquire()  # Grab or wait+grab the lock.

        if self.hosts:
            ip = self.hosts.pop()

        self.lock.release()  # Release the lock, so another thread could grab it.

        return ip

    def dequeue(self):
        while True:
            ip = self.pop_queue()

            if not ip:
                return None

            result = 'alive' if url_ok(ip) else 'dead'
            record = TheModel.query.filter_by(website=ip).first()

            if result == 'alive':

                db.session.query(TheModel).filter(TheModel.website == ip).update({TheModel.found_online_date: datetime.datetime.now()})
                db.session.commit()

                if record.is_offline:

                    # print "-------- NOTIFY USER " + record.user_email + " WEBSITE CAME ONLINE --------"
                    db.session.query(TheModel).filter(TheModel.website == ip).update({TheModel.is_offline: 0})
                    db.session.commit()

                    if (record.notifications_limit > 0) and record.enable_notifications:
                        try:
                            send_notification_email(record.user_email, record.website + " is back online. IsOnlineZilla notifier", "Just letting you know that the website " + record.website + " is back online. ")
                        except Exception, e:
                            print "something went wrong..." + e.message

            if result == 'dead':
                if record.is_offline:
                    pass
                else:
                    db.session.query(TheModel).filter(TheModel.website == ip).update({TheModel.notifications_limit: TheModel.notifications_limit - 1, TheModel.is_offline: 1, TheModel.found_offline_date: datetime.datetime.now()})
                    db.session.commit()

                    # print "-------- NOTIFY USER " + record.user_email + " WEBSITE IS OFFLINE --------"

                    if record.notifications_limit == 5:
                        try:
                            send_notification_email(record.user_email, record.website + " is down. ", "YOU HAVE ONLY  " + record.notifications_limit + " more notifications before they expire!")
                        except Exception, e:
                            print "something went wrong..." + e.message

                    if (record.notifications_limit > 0) and record.enable_notifications:
                        try:
                            send_notification_email(record.user_email, record.website + " is down. IsOnlineZilla notifier", "Just letting you know that the website " + record.website + " is offline @ " + str(datetime.datetime.utcnow()) + " UTC")
                        except Exception, e:
                            print "something went wrong..." + e.message

                    # self.status[result].append(ip)


    def start(self):
        threads = []

        for i in range(self.thread_count):
            # Create self.thread_count number of threads that together will
            # cooperate removing every ip in the list. Each thread will do the
            # job as fast as it can.
            t = threading.Thread(target=self.dequeue)
            t.start()
            threads.append(t)

        # Wait until all the threads are done. .join() is blocking.
        [t.join() for t in threads]

        return self.status  # start = time.time()


mRecords = db.session.query(TheModel).filter(TheModel.is_deleted == 0).all()

ping = Pinger()
ping.thread_count = 4

for mRecord in mRecords:
    ping.hosts.append(mRecord.website)

ping.start()

#print 'It took %.4f seconds' % (time.time() - start)
