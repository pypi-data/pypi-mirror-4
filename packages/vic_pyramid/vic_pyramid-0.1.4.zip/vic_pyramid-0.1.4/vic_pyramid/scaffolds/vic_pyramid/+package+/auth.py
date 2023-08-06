from .models.user import UserModel
    
def get_group(userid, request):
    if userid is not None:
        user_model = UserModel(request.read_session)
        user = user_model.get_user_by_id(userid)
        if user is None:
            return []
        
        result = set(['user', 'user:%s' % user.user_name])
        result |= set(['permission:%s' % p.permission_name 
                       for p in user.permissions])
        result |= set(['group:%s' % g.group_name for g in user.groups])
        return result
    return []