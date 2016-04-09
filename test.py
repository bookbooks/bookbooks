from book_db_access import *
from user_db_access import *
from sqlalchemy import *


DATABASEURI = "postgresql://yc3171:6567@w4111vm.eastus.cloudapp.azure.com/w4111"
engine = create_engine(DATABASEURI)
conn = None
try:
    conn = engine.connect()
except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    conn = None

bda = BookDBAccess(conn)
# print bda.get_reading_list(9, 'read')
# print bda.get_wishlist(9)
# print bda.get_books_from_wishlist(2)
# print bda.get_book_tags(16)
# print bda.get_books_by_tag_id(1)
print bda.get_books_in_shoppingcart(1)

uda = UserDBAccess(conn)
# print uda.get_followers(1)
# print uda.get_followings(1)