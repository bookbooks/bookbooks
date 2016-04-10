class BookDBAccess:
    def __init__(self, conn):
        self.conn = conn

    def get_book(self, book_id):
        book = {}
        cursor = self.conn.execute('select b.*, g.name as genre_name from books b, book_genre bg, genres g where b.bid=bg.bid and bg.gid=g.gid and b.bid=%s', (book_id,))
        for row in cursor:
            book = row
        cursor.close()

        return dict(book)

    def get_books_by_genre(self, genre_id, order='b.name'):
        books = []
        segment = ' order by ' + order
        if int(genre_id) > 0:  # not all
            cursor = self.conn.execute('select b.* from books b, book_genre bg, genres g where b.bid=bg.bid and bg.gid=g.gid and g.gid=%s' + segment, (genre_id, ))
            for row in cursor:
                books.append(row)
            cursor.close()
        else:
            cursor = self.conn.execute('select b.*, g.name as genre_name from books b, book_genre bg, genres g where b.bid=bg.bid and bg.gid=g.gid'  + segment)
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

    def get_wishlist(self, user_id):
        wishlists = []
        cursor = self.conn.execute('select wl.* from wishlists wl where wl.uid=%s', (user_id, ))
        for row in cursor:
            wishlists.append(row)
        cursor.close()

        return wishlists

    def get_books_from_wishlist(self, wishlist_id):
        books = []
        cursor = self.conn.execute('select wb.* from wishlist_book wb where wb.wid=%s', (wishlist_id, ))
        for row in cursor:
            bid = row['bid']
            book = self.get_book(bid)
            books.append(book)
        cursor.close()

        return books

    def get_book_tags(self, book_id):
        tags = []
        cursor = self.conn.execute('select distinct(t.*) from user_tag_book utb, tags t where utb.tid=t.tid and utb.bid=%s', (book_id, ))
        for row in cursor:
            tags.append(row)
        cursor.close()

        return tags

    def get_books_by_tag_id(self, tag_id):
        books = []
        cursor = self.conn.execute('select distinct(utb.bid) from user_tag_book utb where utb.tid=%s', (tag_id, ))
        for row in cursor:
            bid = row['bid']
            book = self.get_book(bid)
            books.append(book)
        cursor.close()

        return books

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