class UserDBAccess:
    def __init__(self, conn):
        self.conn = conn

    def get_user(self, user_id):
        user = {}
        cursor = self.conn.execute('select u.* from users u where u.uid=%s', user_id)
        for row in cursor:
            user = dict(row)
            del user['password']
            if not user['address']:
                user['address'] = ''
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

    def register(self, username, password, firstname, lastname, email):
        output = {'result': {}, 'status': False, 'message': ''}
        status = False
        message = ''
        user = {}

        is_unique, message = self.__is_unique(username, email)
        if not is_unique:
            output['message'] = message
            return output
        else:
            status = True
            cursor = self.conn.execute("""insert into users(username, password, firstname, lastname, email, creationdate)
            values (%s, %s, %s, %s, %s, now()) returning uid, creationdate""", (username, password, firstname, lastname, email))
            for row in cursor:
                new_user_id = row['uid']
                creationdate = row['creationdate']
                user['uid'] = new_user_id
                user['username'] = username
                user['firstname'] = firstname
                user['lastname'] = lastname
                user['email'] = email
                user['creationdate'] = creationdate
            cursor.close()
            output['result'] = user
            output['message'] = 'The registration is successful!'
            output['status'] = status

            return output

    def __is_unique(self, username, email):
        message = 'You can use this username and email!'
        status = True

        cursor = self.conn.execute('select count(*) as size from users where username=%s', (username, ))
        for row in cursor:
            if int(row['size']) > 0:
                status = False
                message = 'The username has been taken!'
        cursor.close()

        if status:
            cursor = self.conn.execute('select count(*) as size from users where email=%s', (email, ))
            for row in cursor:
                if int(row['size']) > 0:
                    status = False
                    message = 'The email has been taken!'
            cursor.close()

        return status, message

    def change_password(self, user_id, old_password, new_password):
        output = {'message': '', 'status': False}
        cursor = self.conn.execute('select count(*) as size from users where password=%s and uid=%s', (old_password, user_id))
        for row in cursor:
            if int(row['size']) > 0:
                output['status'] = True
                output['message'] = 'Your password has been changed!'

                self.conn.execute('update users set password=%s where uid=%s', (new_password, user_id))
            else:
                output['status'] = False
                output['message'] = 'The old password is NOT correct!'
        cursor.close()

        return output

    def update_profile(self, user_id, firstname, lastname, email, address):
        output = {'message': '', 'status': False}
        status, message = self.__is_your_email_unique(user_id, email)
        if not status:
            output['status'] = status
            output['message'] = message
        else:
            output['status'] = status
            output['message'] = 'You have successfully updated your profile!'
            self.conn.execute('update users set firstname=%s, lastname=%s, email=%s, address=%s where uid=%s', (firstname, lastname, email, address, user_id))

        return output

    def __is_your_email_unique(self, user_id, email):
        message = 'You can use this email!'
        status = True

        cursor = self.conn.execute('select count(*) as size from users where email=%s and uid!=%s', (email, user_id))
        for row in cursor:
            if int(row['size']) > 0:
                status = False
                message = 'The email has been taken!'
        cursor.close()

        return status, message