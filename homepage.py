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

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)

def connect_db():
    """Returns a new connection to the sqlite database"""
    return sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)

def init_db():
    """Create the database if it doesn't exist"""
    if not os.path.isfile(app.config['DATABASE']):
        print "DB disappeared, making a new one"
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

def populate_database():
    init_db()
    if data_is_stale():
        load_twitter()
        load_github()
        load_wordpress()
        load_picasa()

def data_is_stale():
    """Find the last entry in the sqlite database to determine if we need to
    refresh the data.  This stops us from pulling them each request"""
    try:
        last_updated = g.db.cursor().execute('select last_refresh from entries order by last_refresh desc limit 1').fetchone()[0]
    except:
        return True

    if not last_updated or (datetime.now() - last_updated).seconds > 10800:
        return True

    return False

def load_twitter():
    twitter = feedparser.parse("http://twitter.com/statuses/user_timeline/14377703.rss")
    g.db.cursor().execute('DELETE FROM entries WHERE source = "twitter"')

    for entry in twitter.entries:
        print entry
        g.db.cursor().execute('INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?, ?)', 
                (None, 
                entry['link'], 
                "http://www.sharms.org/static/twitter_1.png",
                entry['summary'], 
                "twitter", 
                datetime.strptime(entry['updated'][:-6], '%a, %d %b %Y %H:%M:%S'), 
                datetime.now()))
 
    g.db.commit()

def load_picasa():
    picasa = feedparser.parse("http://picasaweb.google.com/data/feed/base/user/thisdyingdream/albumid/5501252408388252785?alt=rss&kind=photo&hl=en_US")
    g.db.cursor().execute('DELETE FROM entries WHERE source = "picasa"')

    for entry in picasa.entries:
        print entry
        g.db.cursor().execute('INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?, ?)', 
                (None, 
                entry['link'], 
                "http://www.sharms.org/static/picture.png",
                entry['media_description'], 
                "picasa", 
                datetime.strptime(entry['updated'][:-6], '%Y-%m-%dT%H:%M:%S'), 
                datetime.now()))
 
    g.db.commit()
 

def load_wordpress():
    wordpress = feedparser.parse("http://www.sharms.org/blog/feed/")
    g.db.cursor().execute('DELETE FROM entries WHERE source = "wordpress"')

    for entry in wordpress.entries:
        print entry
        g.db.cursor().execute('INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?, ?)', 
                (None, 
                entry['link'], 
                "http://www.sharms.org/static/wordpress.png",
                entry['title'], 
                "wordpress", 
                datetime.strptime(entry['updated'][:-6], '%a, %d %b %Y %H:%M:%S'), 
                datetime.now()))
 
    g.db.commit()
    
def load_github():
    github = feedparser.parse("http://github.com/sharms.atom")
    g.db.cursor().execute('DELETE FROM entries WHERE source = "github"')

    for entry in github.entries:
        print entry
        g.db.cursor().execute('INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?, ?)', 
                (None, 
                entry['link'], 
                "http://www.sharms.org/static/cog.png",
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
    results = query_db("select * from entries order by updated desc")
    return render_template('index.html', results = results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443)

