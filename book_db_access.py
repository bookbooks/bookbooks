import sqlalchemy

class BookDBAccess:
    def __init__(self, conn):
        self.conn = conn

    def get_book(self, book_id, get_rating=False):
        book = {}
        cursor = self.conn.execute('select b.*, g.name as genre_name from books b, book_genre bg, genres g where b.bid=bg.bid and bg.gid=g.gid and b.bid=%s', (book_id,))
        for row in cursor:
            book = dict(row)
        cursor.close()

        if get_rating:
            cursor = self.conn.execute('select avg(rating) as avg_rating from readingstatus where bid=%s', book_id)
            for row in cursor:
                if row['avg_rating']:
                    book['rating'] = round(row['avg_rating'], 2)
            cursor.close()

        return book

    def get_books_by_genre(self, genre_id, order='b.name'):
        books = []
        segment = ' and b.deleted=false order by ' + order
        if int(genre_id) > 0:  # not all
            cursor = self.conn.execute('select b.* from books b, book_genre bg, genres g where b.bid=bg.bid and bg.gid=g.gid and g.gid=%s' + segment, (genre_id, ))
            for row in cursor:
                books.append(row)
            cursor.close()
        else:
            cursor = self.conn.execute('select distinct(b.*) from books b, book_genre bg, genres g where b.bid=bg.bid and bg.gid=g.gid'  + segment)
            for row in cursor:
                books.append(row)
            cursor.close()

        return books

    def get_review_by_book_id(self, book_id):
        reviews = []
        cursor = self.conn.execute('select u.*, r.contents, r.reviewdate from books b, users u, reviews r where b.bid=r.bid and u.uid=r.uid and b.bid=%s', book_id)
        for row in cursor:
            reviews.append(row)
        cursor.close()

        return reviews

    def get_reading_list(self, user_id, status):
        books = []
        cursor = self.conn.execute('select rs.* from readingstatus rs where rs.uid=%s and rs.currentstatus=%s', (user_id, status))
        for row in cursor:
            bid = row['bid']
            rating = row['rating']
            book = self.get_book(bid)
            book['rating'] = rating
            books.append(book)
        cursor.close()

        return books

    def get_wishlists(self, user_id):
        wishlists = []
        cursor = self.conn.execute('select wl.* from wishlists wl where wl.uid=%s order by creationdate desc', (user_id, ))
        for row in cursor:
            wishlists.append(row)
        cursor.close()

        return wishlists

    def get_wishlist(self, wishlist_id):
        wishlist = {}
        cursor = self.conn.execute('select wl.* from wishlists wl where wl.wid=%s', (wishlist_id, ))
        for row in cursor:
            wishlist = dict(row)
        cursor.close()

        return wishlist

    def get_books_from_wishlist(self, wishlist_id):
        books = []
        cursor = self.conn.execute('select wb.* from wishlist_book wb where wb.wid=%s', (wishlist_id, ))
        for row in cursor:
            bid = row['bid']
            book = self.get_book(bid)
            books.append(book)
        cursor.close()

        return books

    def add_wishlist(self, user_id, name):
        self.conn.execute('insert into wishlists(name, creationdate, uid) values (%s, now(), %s)', (name, user_id))

    def get_book_tags(self, book_id):
        tags = []
        cursor = self.conn.execute('select distinct(t.*) from user_tag_book utb, tags t where utb.tid=t.tid and utb.bid=%s', (book_id, ))
        for row in cursor:
            tags.append(row)
        cursor.close()

        return tags

    def get_books_by_tag_id(self, tag_id):
        books = []
        tag = ''
        cursor = self.conn.execute('select distinct(utb.bid), t.name from user_tag_book utb, tags t where utb.tid=t.tid and utb.tid=%s', (tag_id, ))
        for row in cursor:
            bid = row['bid']
            tag = row['name']
            book = self.get_book(bid)
            books.append(book)
        cursor.close()

        return books, tag

    def get_genres(self):
        genres = []
        cursor = self.conn.execute('select * from genres order by name')
        for row in cursor:
            genre = dict(row)
            genres.append(genre)
        cursor.close()

        return genres

    def get_genre(self, genre_id):
        genre = {}
        cursor = self.conn.execute('select * from genres where gid=%s', genre_id)
        for row in cursor:
            genre = row
        cursor.close()

        return dict(genre)

    def search(self, keyword):
        books = []
        query = sqlalchemy.text("select * from books where deleted=false and (upper(name) like '%" + keyword.upper() + "%' or upper(author) like '%" + keyword.upper() + "%')")
        cursor = self.conn.execute(query)
        for row in cursor:
            books.append(row)
        cursor.close()

        return books

    def get_newest_book(self, limit):
        books = []
        query = sqlalchemy.text("select * from books where deleted=false order by bid desc limit " + str(limit))
        cursor = self.conn.execute(query)
        for row in cursor:
            books.append(row)
        cursor.close()

        return books

    def get_best_sellers(self, limit):
        books = []
        query = sqlalchemy.text("""select ob.bid, count(ob.*) as num_sale
        from order_book ob, books b
        where b.deleted=false
        and ob.bid=b.bid
        group by ob.bid
        order by num_sale desc
        limit """ + str(limit))
        cursor = self.conn.execute(query)
        for row in cursor:
            bid = row['bid']
            book = self.get_book(bid)
            book['num_sale'] = row['num_sale']
            books.append(book)
        cursor.close()

        return books