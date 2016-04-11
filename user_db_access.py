class UserDBAccess:
    def __init__(self, conn):
        self.conn = conn

    def get_user(self, user_id):
        user = {}
        cursor = self.conn.execute('select u.* from users u where u.uid=%s', user_id)
        for row in cursor:
            user = dict(row)
            del user['password']
        cursor.close()

        return dict(user)

    def get_followers(self, user_id, only_id=False):  # get the users that follow you
        followers = []
        cursor = self.conn.execute('select f.uid from follows f where f.followid=%s', user_id)
        for row in cursor:
            uid = row['uid']
            if only_id:
                followers.append(uid)
            else:
                user = self.get_user(uid)
                followers.append(user)
        cursor.close()

        return followers

    def get_followings(self, user_id):  # get the users that you are following
        followings = []
        cursor = self.conn.execute('select f.followid from follows f where f.uid=%s', user_id)
        for row in cursor:
            follow_id = row['followid']
            user = self.get_user(follow_id)
            followings.append(user)
        cursor.close()

        return followings

    def follow(self, your_id, his_id):
        try:
            self.conn.execute('insert into follows values(%s, %s)', (your_id, his_id))
        except Exception as e:
            print e

    def unfollow(self, your_id, his_id):
        try:
            self.conn.execute('delete from follows where uid=%s and followid=%s', (your_id, his_id))
        except Exception as e:
            print e

