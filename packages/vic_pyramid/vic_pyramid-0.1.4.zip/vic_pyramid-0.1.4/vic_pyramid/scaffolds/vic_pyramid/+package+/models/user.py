import logging

from . import tables

class AuthError(Exception):
    """Authentication error
    
    """

class BadPassword(AuthError):
    """Raised when user tries to authenticate with wrong password
    
    """

class UserNotExist(AuthError):
    """Raised when user tries to authenticate with a non-exist user
    
    """

class UserModel(object):
    """User data model
    
    """
    
    def __init__(self, session, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.session = session
        
    def get_user_by_name(self, user_name):
        """Get a user by name
        
        """
        user = self.session \
            .query(tables.User) \
            .filter_by(user_name=unicode(user_name)) \
            .first()
        return user
    
    def get_user_by_id(self, user_id):
        """Get a user by ID
        
        """
        user = self.session.query(tables.User).get(int(user_id))
        return user
    
    def get_user_by_email(self, email):
        """Get a user by email
        
        """
        user = self.session \
            .query(tables.User) \
            .filter_by(email=unicode(email)) \
            .first()
        return user
    
    def get_user_by_ids(self, user_ids):
        """Get users by ID list
        
        if follow_list_order is true, the order will be returned as the order
        of user_ids
        
        """
        User = tables.User
        users = self.session.query(User) \
            .filter(User.user_id.in_(user_ids))
        return users
    
    def get_users(self):
        """Get users
        
        """
        query = self.session.query(tables.User)
        return query
    
    def query_user(self, user_id=None, user_name=None, email=None):
        """Query user by different conditions
        
        """
        query = self.session.query(tables.User)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        if user_name is not None:
            query = query.filter_by(user_name=user_name)
        if email is not None:
            query = query.filter_by(email=email)
        return query.first()
    
    def create_user(
        self, 
        user_name, 
        display_name,
        password,
        email,
    ):
        """Create a new user and return verification
        
        """
        user_name = user_name.lower()
        email = email.lower()
        salt_hashedpassword = ''.join(self.get_salt_hashedpassword(password))
        
        # create user
        user = tables.User(
            user_name=unicode(user_name), 
            email=unicode(email), 
            display_name=unicode(display_name), 
            password=salt_hashedpassword,
            created=tables.now_func()
        )
        self.session.add(user)
        # flush the change, so we can get real user id
        self.session.flush()
        assert user.user_id is not None, 'User id should not be none here'
        user_id = user.user_id
        
        self.logger.info('Create user %s', user_name)
        return user_id
    
    def get_salt_hashedpassword(self, password):
        """Generate salt and hashed password, 
        
        salt is a 160bits random string, this is meant to protect the hashed
        password from query table attack
        
        hashedpassword is SHA1(password, salt)
        
        return value is (hexdigest of salt, hexdigest of hashedpassword)
        """
        import os
        import hashlib
        if isinstance(password, unicode):
            password_utf8 = password.encode('utf8')
        else:
            password_utf8 = password

        # generate salt
        salt = hashlib.sha1()
        # NOTICE: notice, os.urandom uses /dev/urandom under Linux
        # this function call will get blocked if there is no available
        # random bytes in /dev/urandom. An attacker could perform a
        # DOS attack based on this factor
        salt.update(os.urandom(16))
        
        # generate hashed password
        hashedpassword = hashlib.sha1()
        hashedpassword.update(password_utf8 + salt.hexdigest())
        
        return salt.hexdigest(), hashedpassword.hexdigest()
    
    def validate_password(self, user_id, password):
        """Validate password of a user
        
        """
        import hashlib
        user = self.get_user_by_id(user_id)
        if user is None:
            raise UserNotExist
        
        salt_hashedpassword = user.password
        salt = salt_hashedpassword[:40]
        hashedpassword = salt_hashedpassword[40:]
        
        input_hashedpassword = hashlib.sha1(password + salt).hexdigest()
        return hashedpassword == input_hashedpassword
    
    def authenticate_user(self, name_or_email, password):
        """Authenticate user by user_name of email and password. If the user
        pass the authentication, return user_id, otherwise, raise error
        
        """
        from sqlalchemy.sql.expression import or_
        User = tables.User
        user = self.session.query(User) \
            .filter(or_(User.user_name==name_or_email,
                        User.email==name_or_email)) \
            .first()
        if user is None:
            # maybe it's case problem, although we enforce lower case to
            # user name and email now, but it seems there is still some
            # accounts have id in different cases, so that's why we do the
            # user query twice
            name_or_email = name_or_email.lower()
            user = self.session.query(User) \
                .filter(or_(User.user_name==name_or_email,
                            User.email==name_or_email)) \
                .first()
            if user is None:
                raise UserNotExist('User %s does not exist' % name_or_email)
        if not self.validate_password(user.user_id, password):
            raise BadPassword('Bad password')
        return user.user_id

    def update_password(self, user_id, password):
        """Update password of an user
        
        """
        user = self.get_user_by_id(user_id)
        if user is None:
            raise KeyError
        salt_hashedpassword = ''.join(self.get_salt_hashedpassword(password))
        user.password = salt_hashedpassword
        self.session.add(user)
        
    def update_user(self, user_id, **kwargs):
        """Update attributes of a user
        
        """
        user = self.get_user_by_id(user_id)
        if user is None:
            raise KeyError
        if 'display_name' in kwargs:
            user.display_name = kwargs['display_name']
        if 'email' in kwargs:
            user.email = kwargs['email']
        self.session.add(user)
    
    def update_groups(self, user_id, group_ids):
        """Update groups of this user
        
        """
        user = self.get_user_by_id(user_id)
        new_groups = self.session \
            .query(tables.Group) \
            .filter(tables.Group.group_id.in_(group_ids))
        user.groups = new_groups.all()
        self.session.flush()