import unittest

class TestGroupModel(unittest.TestCase):
    
    def setUp(self):
        import datetime
        from .helper import create_session
        from ..models import tables
        tables.set_now_func(datetime.datetime.utcnow)
        self.session = create_session(zope_transaction=True)
        
    def tearDown(self):
        self.session.remove()
        
    def make_one(self):
        from ..models.group import GroupModel
        return GroupModel(self.session)
    
    def make_permission_model(self):
        from ..models.permission import PermissionModel
        return PermissionModel(self.session)
    
    def test_create_group(self):
        import transaction
        model = self.make_one()
        
        group_name = 'tester'
        display_name = group_name
        
        with transaction.manager:
            group_id = model.create_group(
                group_name=group_name,
                display_name=display_name,
            )
        group = model.get_group_by_id(group_id)
        
        self.assertEqual(group.group_name, group_name)
        self.assertEqual(group.display_name, display_name)
        
    def test_update_permissions(self):
        import transaction
        model = self.make_one()
        permission_model = self.make_permission_model()
        
        group_name = 'tester'
        display_name = group_name
        
        with transaction.manager:
            group_id = model.create_group(
                group_name=group_name,
                display_name=display_name,
            )
            pid1 = permission_model.create_permission('p1')
            pid2 = permission_model.create_permission('p2')
            pid3 = permission_model.create_permission('p3')
            
        group = model.get_group_by_id(group_id)
        pids = set([p.permission_id for p in group.permissions])
        self.assertEqual(pids, set([]))
            
        def assert_update(new_permissions):
            with transaction.manager:
                model.update_permissions(group_id, new_permissions)
            group = model.get_group_by_id(group_id)
            pids = set([p.permission_id for p in group.permissions])
            self.assertEqual(pids, set(new_permissions))
        
        assert_update([pid1])
        assert_update([pid1, pid2])
        assert_update([pid1, pid2, pid3])
        assert_update([pid1, pid3])
        assert_update([pid1])
        assert_update([])
        assert_update([pid1])
    
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGroupModel))
    return suite
        
if __name__ == '__main__':
    unittest.main(defaultTest='suite')