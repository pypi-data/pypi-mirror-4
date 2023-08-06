import unittest
from collagram import Collage


USER = 'adamrt'
USER_ID = '19226776'
TAG = 'vurbranch'
BAD_USER = 'jfjfjfjfjfjfjfjfij'
PATH_USERS = '/srv/www/collagram.com/media/users/'
PATH_TAGS = '/srv/www/collagram.com/media/tags/'


class TestCollage(unittest.TestCase):

    def setUp(self):
        self.user = Collage(username=USER)
        self.bad_user = Collage(username=BAD_USER)
        self.tag = Collage(tag=TAG)
        self.size = Collage(username=USER, columns=4, rows=4)
        self.user_path = Collage(username=USER, path_users=PATH_USERS)
        self.tag_path = Collage(tag=TAG, path_tags=PATH_TAGS)

    def test_attributes(self):
        self.assertRaises(AttributeError, Collage)
        self.assertRaises(AttributeError, Collage,
                          username=USER,
                          tag=TAG)

    def test_columns_and_rows(self):
        self.assertEqual(self.user.columns, 10)
        self.assertEqual(self.user.rows, 2)

        self.assertEqual(self.size.columns, 4)
        self.assertEqual(self.size.rows, 4)

    def test_name(self):
        self.assertEqual(self.user.name, '@' + USER)
        self.assertEqual(self.tag.name, '#' + TAG)

    def test_user_id(self):
        self.assertEqual(self.user.user_id, USER_ID)
        self.assertEqual(self.bad_user.user_id, None)
        self.assertEqual(self.tag.user_id, None)

    def test_filename(self):
        assert self.user.filename.endswith('users/' + USER + '.jpg')
        self.assertEqual(self.user_path.filename, PATH_USERS + USER + '.jpg')

    def test_dimensions(self):
        self.assertEqual(self.user.width, 1500)
        self.assertEqual(self.user.height, 300)

if __name__ == '__main__':
    unittest.main()
