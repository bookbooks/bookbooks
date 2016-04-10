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
  return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")
    
@app.route('/userLogin', methods=['POST'])
def userLogin():
    username = request.form['username']
    password = request.form['password']
    result = g.conn.execute("SELECT * FROM users WHERE username = %s and password = %s", (username, password))
    for row in result:
        session['uid'] = row['uid']
        session['username'] = row['username']
        session['firstname'] = row['firstname']
        session['lastname'] = row['lastname']
        session['email'] = row['email']
        return redirect('/')

    return redirect('/login')

@app.route('/books/<genre_id>')
def list_books(genre_id):
    bda = BookDBAccess(g.conn)
    books = bda.get_books_by_genre(genre_id)

    genre = {'name': 'All books'}
    if int(genre_id) > 0:
        genre = bda.get_genre(genre_id)

    context = dict(data=books, genre=genre)

    return render_template("books.html", **context)

@app.route('/book/<book_id>')
def display_book(book_id):
    book = {}
    reviews = []

    bda = BookDBAccess(g.conn)
    book = bda.get_book(book_id)
    reviews = bda.get_review_by_book_id(book_id)

    context = dict(book=book, reviews=reviews)

    return render_template("book.html", **context)

@app.route('/user/<user_id>')
def display_user(user_id):
    followings = []
    followers = []

@app.route('/shoppingcart')
def display_shoppingcart():
    if session and 'uid' in session:
        user_id = session['uid']
        oda = OrderDBAccess(g.conn)
        books, total_price = oda.get_books_in_shoppingcart(user_id)

        context = dict(books=books, total_price=total_price)

        return render_template("shoppingcart.html", **context)
    else:
        return redirect('/login')

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
        return redirect('/login')

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
        return redirect('/login')

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
