import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ..models import tables
from ..models import setup_database

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    import getpass
    import transaction
    from ..models.user import UserModel
    from ..models.group import GroupModel
    from ..models.permission import PermissionModel
    
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    
    # create all tables
    settings = setup_database({}, **settings)
    engine = settings['write_engine']
    tables.DeclarativeBase.metadata.create_all(engine)
    
    session = settings['write_session_maker']()
    user_model = UserModel(session)
    group_model = GroupModel(session)
    permission_model = PermissionModel(session)
    
    with transaction.manager:
        admin = user_model.get_user_by_name('admin')
        if admin is None:
            print 'Create admin account'
            
            email = raw_input('Email:')
            
            password = getpass.getpass('Password:')
            confirm = getpass.getpass('Confirm:')
            if password != confirm:
                print 'Password not match'
                return
        
            user_id = user_model.create_user(
                user_name='admin',
                display_name='Administrator',
                email=email,
                password=password
            )
            admin = user_model.get_user_by_id(user_id)
            session.flush()
            print 'Created admin, user_id=%s' % admin.user_id
            
        permission = permission_model.get_permission_by_name('admin')
        if permission is None:
            print 'Create admin permission ...'
            permission_model.create_permission(
                permission_name='admin',
                description='Administrate',
            )
            permission = permission_model.get_permission_by_name('admin')
            
        group = group_model.get_group_by_name('admin')
        if group is None:
            print 'Create admin group ...'
            group_model.create_group(
                group_name='admin',
                display_name='Administrators',
            )
            group = group_model.get_group_by_name('admin')
            
        print 'Add admin permission to admin group'
        group_model.update_permissions(group.group_id, [permission.permission_id])
        session.flush()
            
        print 'Add admin to admin group'
        user_model.update_groups(admin.user_id, [group.group_id])
        session.flush()
            