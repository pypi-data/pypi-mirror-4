import unittest

import dm.util.db


class DatabaseTest(unittest.TestCase):
    """
    WARNING: once we run any command that creates a db connection
    any following stuff will break because you can't delete/create db
    
    Thus this test can *not* be run through the standard dm test runner because
    the test runner initialises the dm application which in turn creates a
    connection to the database.

    In any case these tests should not be run as part of the normal test suite
    as they are testing actions that only take place from the command line and
    which result in the deletion and creation of the database

    """

    def setUp(self):
        self.db = dm.util.db.Database()
        try:
            self.db.delete()
        except Exception, inst:
            msg = \
'''
DatabaseTest.setUp(): Attempt to delete db to ensure a clean start failed.
This need *not* indicate an error (for example the db may not exist) but please
check the following error message:

%s''' % inst
            print msg
        self.db.create()

    def test_delete(self):
        self.db.delete()
        # verify deletion?

    def test_init(self):
        self.db.init()

    def test_rebuild(self):
        self.db.rebuild()

    def test_rebuild_when_db_does_not_exist(self):
        self.db.delete()
        self.db.rebuild()

if __name__ == '__main__':
    # need to fix this as otherwise loading of system dictionary fails
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'dm.django.settings.main'
    unittest.main()
