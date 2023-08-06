__author__ = 'Philipp Rautenberg'
import datetime as dt

import sqlalchemy as sa

import flask
import flask.ext.sqlalchemy
import flask.ext.restless

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from email import utils

app = flask.Flask(__name__)

app.config['DEBUG'] = True
app.config.from_object('config')
db = flask.ext.sqlalchemy.SQLAlchemy(app)

class SMTPFactory(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_smtp_connection(self):
        return smtplib.SMTP(self.host, self.port)

smtp_factory = SMTPFactory(app.config['SMTP_SERVER'], app.config['SMTP_SERVER_PORT'])

def send_email(mapper, connection, query):
    msg = MIMEMultipart()
    msg['From'] = query.header_from
    msg['To'] = query.header_to.replace(',', ';')
    msg['CC'] = query.header_cc
    msg['Date'] = utils.formatdate( time.mktime(query.date.timetuple()) )
    msg['Subject'] = query.header_subject

    msg.attach( MIMEText( "(%s '%s')\n\n\n%s" %(
        app.config['SERVICE_PREAMBLE'],
        query.service,
        query.content),
        'plain'))

    if query.header_reply_to != "":
        msg.add_header('reply-to', query.header_reply_to)

    try:
        s = smtp_factory.get_smtp_connection()
        s.set_debuglevel(0)
        s.starttls()
        s.sendmail(msg['From'], msg['To'].split(";"), msg.as_string())
        s.quit()
    except Exception, e:
        print e, "Error sending an email."


class Message(db.Model):
    __tablename__ = 'messages'
    if app.config.has_key("SCHEMA"):
        __table_args__ = (
            {
                'schema': app.config['SCHEMA'],
                })
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.Unicode, nullable=False)
    header_from = db.Column(db.Unicode, nullable=False, default=app.config['FROM_DEFAULT'])
    header_to = db.Column(db.Unicode, nullable=False)
    header_cc = db.Column(db.Unicode)
    header_reply_to = db.Column(db.Unicode, default=u'')
    header_subject = db.Column(db.Unicode)
    content = db.Column(db.Unicode)
    date = db.Column(db.DateTime, default=dt.datetime.now)

sa.event.listen(Message, 'after_insert', send_email)

if __name__ == '__main__':
    db.create_all()
    manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
    manager.create_api(
        Message,
        methods=['GET', 'POST'],
        )
    app.run()