# -*- coding: utf-8 -*-
"""
    HomePage
    --------

    How my homepage reads RSS feeds and puts them in one place

    :copyright: (c) 2010 by Steven Harms
    :license: BSD
"""

from flask import Flask,request,render_template,abort,g
from flask import g
import sqlite3
import time
import os.path
import feedparser
from datetime import datetime


DATABASE = '/var/tmp/sharms-homepage-cache.sqlite'
DEBUG = True
SECRET_KEY = 'ksd241241kndkndk1ndk123442ievjfiee'
HOST = '0.0.0.0'
port = '443'

app = Flask(__name__)
print app
app.config.from_object(__name__)

def connect_db():
    """Returns a new connection to the sqlite database"""
    return sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)

def init_db():
    """Create the database if it doesn't exist"""
    if not os.path.isfile(app.config['DATABASE']):
        f = app.open_resource('schema.sql')
        db = connect_db()
        db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one = False):
    """Query database returning dictionary"""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
        for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def format_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

def populate_database():
    if data_is_stale():
        load_twitter()
        load_github()

def data_is_stale():
    """Find the last entry in the sqlite database to determine if we need to
    refresh the data.  This stops us from pulling them each request"""
    last_updated = g.db.cursor().execute('select last_refresh from entries order by last_refresh desc limit 1').fetchone()[0]
    if (datetime.now() - last_updated).seconds > 5000:
        return True
    return False

def load_twitter():
    twitter = feedparser.parse("http://twitter.com/statuses/user_timeline/14377703.rss")
    g.db.cursor().execute('DELETE FROM entries WHERE source = "twitter"')

    for entry in twitter.entries:
        print entry
        g.db.cursor().execute('INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?)', 
                (None, 
                entry['link'], 
                entry['summary'], 
                "twitter", 
                datetime.strptime(entry['updated'][:-6], '%a, %d %b %Y %H:%M:%S'), 
                datetime.now()))
 
    g.db.commit()
    
def load_github():
    github = feedparser.parse("http://github.com/sharms.atom")
    g.db.cursor().execute('DELETE FROM entries WHERE source = "github"')

    for entry in github.entries:
        print entry
        g.db.cursor().execute('INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?)', 
                (None, 
                entry['link'], 
                entry['title'], 
                "github", 
                datetime.strptime(entry['updated'][:-6], '%Y-%m-%dT%H:%M:%S'), 
                datetime.now()))
 
    g.db.commit()
 
@app.before_request
def before_request():
    init_db()
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/')
def index():
    populate_database()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443)

