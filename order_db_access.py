from book_db_access import *

class OrderDBAccess:
    def __init__(self, conn):
        self.conn = conn

    def get_books_in_shoppingcart(self, user_id):
        bda = BookDBAccess(self.conn)
        books = []
        cursor = self.conn.execute('select sc.* from shoppingcarts sc where sc.uid=%s and sc.status=true', (user_id, ))
        for row in cursor:
            bid = row['bid']
            quantity = row['quantity']
            book = bda.get_book(bid)
            book['quantity'] = quantity
            books.append(book)
        cursor.close()

        return books

    def remove_book_from_shoppingcart(self, book_id, user_id):
        self.conn.execute('update shoppingcarts set status=false where bid=%s and uid=%s', (book_id, user_id))

    def insert_book_to_shoppingcart(self, book_id, user_id, quantity):
        existed = False
        cursor = self.conn.execute('select count(*) as size from shoppingcarts where bid=%s and uid=%s', (book_id, user_id))
        for row in cursor:
            count = row['size']
            if count > 0:
                existed = True
                result = self.conn.execute('select * from shoppingcarts where bid=%s and uid=%s', (book_id, user_id))
                for r in result:
                    status = r['status']
                    if not status:
                        self.conn.execute('update shoppingcarts set status=true, quantity=%s where bid=%s and uid=%s', (quantity, book_id, user_id))
                    else:
                        quantity = r['quantity'] + quantity
                        self.update_quantity_for_book_in_shoppingcart(book_id, user_id, quantity)
                result.close()
            else:
                self.conn.execute('insert into shoppingcarts values(%s, %s, true, %s)', (user_id, book_id, quantity))
        cursor.close()

        return existed

    def update_quantity_for_book_in_shoppingcart(self, book_id, user_id, quantity):
        self.conn.execute('update shoppingcarts set quantity=%s where bid=%s and uid=%s', (quantity, book_id, user_id))

    def create_order(self, user_id, address, mobile, firstname, lastname, books):
        rslt_id = self.conn.execute("""insert into orders (orderdate, address, buyer, mobile, firstname, lastname)
        values (now(), %s, %s, %s, %s, %s) RETURNING oid""", (address, user_id, mobile, firstname, lastname))
        for row in rslt_id:
            order_id = row['oid']
            print 'new oid: ' + str(order_id)
            self.__create_orderline(order_id, books)

    def __create_orderline(self, order_id, books):
        for book in books:
            bid = book['bid']
            quantity = book['quantity']
            self.conn.execute("insert into order_book values (%s, %s, %s)", (order_id, bid, quantity))

    def get_order(self, order_id):
        order = {}
        cursor = self.conn.execute("""select * from orders where oid=%s""", order_id)
        for row in cursor:
            books = self.__get_orderlines(order_id)
            order = dict(row)
            order['books'] = books
        cursor.close()

        return order

    def __get_orderlines(self, order_id):
        books = []
        bda = BookDBAccess(self.conn)
        cursor = self.conn.execute('select * from order_book where oid=%s', (order_id, ))
        for row in cursor:
            bid = row['bid']
            book = bda.get_book(bid)
            book['quantity'] = row['quantity']
            books.append(book)
        cursor.close()

        return books