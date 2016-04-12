#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import click
from sqlalchemy import *
from flask import Flask, request, render_template, g, redirect, Response, session
from book_db_access import *
from user_db_access import *
from order_db_access import *
import urllib


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111a.eastus.cloudapp.azure.com/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@w4111a.eastus.cloudapp.azure.com/proj1part2"
#
DATABASEURI = "postgresql://yc3171:6567@w4111vm.eastus.cloudapp.azure.com/w4111"



#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  # if ('uid' not in session) and (request.endpoint != "login") and (request.endpoint != "userLogin"):
  #   return redirect('/login')
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    bda = BookDBAccess(g.conn)
    newest_books = bda.get_newest_book(8)
    best_sellers = bda.get_best_sellers(8)
    context = dict(newest_books=newest_books, best_sellers=best_sellers)

    return render_template("index.html", **context)

@app.route('/login')
def login():
    requested_url = request.args.get('requested_url')
    message = request.args.get('message')
    error = request.args.get('error')
    context = dict(requested_url=requested_url, message=message, error=error)

    return render_template("login.html", **context)

@app.route('/logout')
def logout():
    session.pop('uid', None)
    session.pop('username', None)
    session.pop('firstname', None)
    session.pop('lastname', None)
    session.pop('email', None)

    return redirect('/')

@app.route('/userLogin', methods=['POST'])
def userLogin():
    username = request.form['username']
    password = request.form['password']
    requested_url = request.form['requested_url']
    result = g.conn.execute("SELECT * FROM users WHERE username = %s and password = %s", (username, password))
    for row in result:
        session['uid'] = row['uid']
        session['username'] = row['username']
        session['firstname'] = row['firstname']
        session['lastname'] = row['lastname']
        session['email'] = row['email']

        if not requested_url or requested_url == 'None':
            return redirect('/')
        else:
            return redirect(urllib.unquote(requested_url))

    return redirect('/login?error=true')

@app.route('/register')
def register():
    refill = {}
    if request.args.get('message'):
        refill['error_message'] = urllib.unquote(request.args.get('message'))
    if request.args.get('username'):
        refill['username'] = urllib.unquote(request.args.get('username'))
    if request.args.get('firstname'):
        refill['firstname'] = urllib.unquote(request.args.get('firstname'))
    if request.args.get('lastname'):
        refill['lastname'] = urllib.unquote(request.args.get('lastname'))
    if request.args.get('email'):
        refill['email'] = urllib.unquote(request.args.get('email'))
    context = dict(refill=refill)

    return render_template("register.html", **context)

@app.route('/settings')
def settings():
    if session and 'uid' in session:
        user_id = session['uid']
        output = {}
        if request.args.get('message'):
            output['message'] = urllib.unquote(request.args.get('message'))
        if request.args.get('status'):
            output['status'] = request.args.get('status')
        if request.args.get('method'):
            output['method'] = urllib.unquote(request.args.get('method'))

        uda = UserDBAccess(g.conn)
        user = uda.get_user(user_id)
        output['user'] = user

        context = dict(output=output)
        return render_template("settings.html", **context)
    else:
        requested_url = '?requested_url=' + urllib.quote(request.url)
        return redirect('/login' + requested_url)


@app.route('/userProcess', methods=['POST'])
def userProcess():
    method = request.form['method']

    uda = UserDBAccess(g.conn)
    if method == 'reg':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        output = uda.register(username, password, firstname, lastname, email)

        if output['status']:
            return redirect('/login?message=' + urllib.quote(output['message']))
        else:
            return redirect('/register?message=%s&username=%s&firstname=%s&lastname=%s&email=%s' % (urllib.quote(output['message']), urllib.quote(username), urllib.quote(firstname), urllib.quote(lastname), urllib.quote(email)))
    elif method == 'changePassword':
        if session and 'uid' in session:
            user_id = session['uid']
            old_password = request.form['old_password']
            new_password = request.form['new_password']
            output = uda.change_password(user_id, old_password, new_password)
            return redirect('/settings?method=%s&status=%s&message=%s' % (urllib.quote(method), output['status'], urllib.quote(output['message'])))
        else:
            redirect('/login')
    else:
        if session and 'uid' in session:
            user_id = session['uid']
            address = request.form['address']
            email = request.form['email']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            output = uda.update_profile(user_id, firstname, lastname, email, address)
            return redirect('/settings?method=%s&status=%s&message=%s' % (urllib.quote(method), output['status'], urllib.quote(output['message'])))
        else:
            redirect('/login')

@app.route('/books/<genre_id>')
def list_books(genre_id):
    bda = BookDBAccess(g.conn)
    books = bda.get_books_by_genre(genre_id)

    genre = {'name': 'All books'}
    if int(genre_id) > 0:
        genre = bda.get_genre(genre_id)

    context = dict(data=books, genre=genre)

    return render_template("books.html", **context)

@app.route('/search', methods=['get'])
def search():
    bda = BookDBAccess(g.conn)
    keyword = request.args.get('keyword')
    books = bda.search(keyword)
    context = dict(data=books, keyword=keyword)

    return render_template("search.html", **context)

@app.route('/book/<book_id>')
def display_book(book_id):
    book = {}
    reviews = []

    bda = BookDBAccess(g.conn)
    book = bda.get_book(book_id)
    reviews = bda.get_review_by_book_id(book_id)

    context = dict(book=book, reviews=reviews)

    return render_template("book.html", **context)

@app.route('/profile')
def profile():
    if session and 'uid' in session:
        user_id = session['uid']
        uda = UserDBAccess(g.conn)
        bda = BookDBAccess(g.conn)

        user = uda.get_user(user_id)
        followings = uda.get_followings(user_id)
        followers = uda.get_followers(user_id, True)
        reading_list = bda.get_reading_list(user_id, 'reading')
        read_list = bda.get_reading_list(user_id, 'read')
        wishlists = bda.get_wishlists(user_id)

        context = dict(user=user, followings=followings, followers=followers, reading_list=reading_list, read_list=read_list, wishlists=wishlists)

        return render_template("profile.html", **context)
    else:
        requested_url = '?requested_url=' + urllib.quote(request.url)
        return redirect('/login' + requested_url)

@app.route('/profile/<user_id>')
def user_profile(user_id):
    uda = UserDBAccess(g.conn)
    bda = BookDBAccess(g.conn)

    user = uda.get_user(user_id)
    followings = uda.get_followings(user_id)
    followers = uda.get_followers(user_id, True)
    reading_list = bda.get_reading_list(user_id, 'reading')
    read_list = bda.get_reading_list(user_id, 'read')
    wishlists = bda.get_wishlists(user_id)

    context = dict(user=user, followings=followings, followers=followers, reading_list=reading_list, read_list=read_list, wishlists=wishlists)

    return render_template("profile.html", **context)

@app.route('/wlProcess', methods=['POST'])
def wishlist_process():
    if session and 'uid' in session:
        user_id = session['uid']
        bda = BookDBAccess(g.conn)
        method = request.form['method']

        if method == 'add_wishlist':
            name = request.form['name']
            bda.add_wishlist(user_id, name)

            return redirect('/profile')
    else:
        return redirect('/login')

@app.route('/addWishlist')
def add_wishlist():
    if session and 'uid' in session:
        user_id = session['uid']

        return render_template("add_wishlist.html")
    else:
        requested_url = '?requested_url=' + urllib.quote(request.url)
        return redirect('/login' + requested_url)

@app.route('/wishlist/<wishlist_id>')
def display_wishlist(wishlist_id):
    bda = BookDBAccess(g.conn)
    books = bda.get_books_from_wishlist(wishlist_id)
    wishlist = bda.get_wishlist(wishlist_id)
    context = dict(data=books, wishlist=wishlist)

    return render_template("wishlist.html", **context)

@app.route('/followProcess', methods=['POST'])
def follow_process():
    if session and 'uid' in session:
        user_id = session['uid']
        method = request.form['method']
        his_id = request.form['his_id']
        uda = UserDBAccess(g.conn)

        if method == 'follow':
            uda.follow(user_id, his_id)
        else:
            uda.unfollow(user_id, his_id)

        return redirect('/profile/' + his_id)
    else:
        return redirect('/login')

@app.route('/followings/<user_id>')
def display_followings(user_id):
    uda = UserDBAccess(g.conn)
    followings = uda.get_followings(user_id)
    user = uda.get_user(user_id)

    context = dict(followings=followings, user=user)

    return render_template("followings.html", **context)

@app.route('/followers/<user_id>')
def display_followers(user_id):
    uda = UserDBAccess(g.conn)
    followers = uda.get_followers(user_id)
    user = uda.get_user(user_id)

    context = dict(followers=followers, user=user)

    return render_template("followers.html", **context)

@app.route('/shoppingcart')
def display_shoppingcart():
    if session and 'uid' in session:
        user_id = session['uid']
        oda = OrderDBAccess(g.conn)
        books, total_price = oda.get_books_in_shoppingcart(user_id)

        context = dict(books=books, total_price=total_price)

        return render_template("shoppingcart.html", **context)
    else:
        requested_url = '?requested_url=' + urllib.quote(request.url)
        return redirect('/login' + requested_url)

@app.route('/scProcess', methods=['POST'])
def shoppingcart_process():
    if session and 'uid' in session:
        user_id = session['uid']
        bid = request.form['bid']
        method = request.form['method']
        oda = OrderDBAccess(g.conn)
        if method == 'remove':
            oda.remove_book_from_shoppingcart(bid, user_id)
        elif method == 'updateQuantity':
            quantity = request.form['quantity']
            oda.update_quantity_for_book_in_shoppingcart(bid, user_id, quantity)

        return redirect('/shoppingcart')
    else:
        return redirect('/login')

@app.route('/orderForm')
def order_form():
    if session and 'uid' in session:
        user_id = session['uid']
        oda = OrderDBAccess(g.conn)
        books, total_price = oda.get_books_in_shoppingcart(user_id)

        context = dict(books=books, total_price=total_price)

        return render_template("order_form.html", **context)
    else:
        requested_url = '?requested_url=' + urllib.quote(request.url)
        return redirect('/login' + requested_url)

@app.route('/orderProcess', methods=['POST'])
def order_process():
    if session and 'uid' in session:
        user_id = session['uid']
        oda = OrderDBAccess(g.conn)
        books, total_price = oda.get_books_in_shoppingcart(user_id)

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        mobile = request.form['mobile']
        address = request.form['address']
        apt = request.form['apt']
        city = request.form['city']
        postcode = request.form['postcode']
        state = request.form['state']
        country = request.form['country']

        address = address + ', Apt ' + apt + '\n'+ city + ', ' + state + ' ' + postcode + '\n' + country

        oda.create_order(user_id, address, mobile, firstname, lastname, books)

        # after the order is created, the shopping cart should be empty
        oda.empty_shoppingcart(user_id)

        return redirect('/orders')
    else:
        return redirect('/login')

@app.route('/orders')
def list_orders():
    if session and 'uid' in session:
        user_id = session['uid']
        oda = OrderDBAccess(g.conn)
        orders = oda.get_orders(user_id)

        context = dict(orders=orders)

        return render_template("orders.html", **context)
    else:
        requested_url = '?requested_url=' + urllib.quote(request.url)
        return redirect('/login' + requested_url)

# method for rendering the sidebar
def list_genres():
    bda = BookDBAccess(g.conn)
    genres = bda.get_genres()
    genres.insert(0,
        {
            'gid': 0,
            'name': 'All books'
        }
    )

    return genres
app.jinja_env.globals.update(list_genres=list_genres)


if __name__ == "__main__":

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
            This function handles command line parameters.
            Run the server using:
            python server.py

            Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
    run()
