import ptah
from ptah.testing import PtahTestCase


class TestCrowdApplication(PtahTestCase):

    _includes = ('ptahcrowd',)

    def _test_crowd_app_add_user(self):
        import ptahcrowd

        user = ptahcrowd.CrowdUser()
        factory.add(user)

        self.assertEqual(user.__name__, str(user.__id__))

    def test_crowd_allowed(self):
        from ptahcrowd.provider import get_allowed_content_types

        self.assertEqual(get_allowed_content_types(None), ('ptah-crowd-user',))


class TestProvider(PtahTestCase):

    _includes = ('ptahcrowd',)

    def test_authenticate(self):
        from ptahcrowd.provider import \
             CrowdAuthProvider, CrowdUser

        provider = CrowdAuthProvider()

        self.assertFalse(
            provider.authenticate(
                {'login': 'test', 'password': '12345'}))

        user = CrowdUser(name='test',
                         login='test',
                         email='test@ptahproject.org',
                         password=ptah.pwd_tool.encode('12345'))
        ptah.get_session().add(user)
        ptah.get_session().flush()

        self.assertTrue(
            provider.authenticate(
                {'login': 'test', 'password': '12345'}))

        self.assertFalse(
            provider.authenticate(
                {'login': 'test', 'password': '56789'}))


    def test_get_bylogin(self):
        from ptahcrowd.provider import \
             CrowdAuthProvider, CrowdUser

        provider = CrowdAuthProvider()
        self.assertIsNone(provider.get_principal_bylogin('test'))

        user = CrowdUser(name='test', login='test',
                         email='test@ptahproject.org',
                         password=ptah.pwd_tool.encode('12345'))
        ptah.get_session().add(user)
        ptah.get_session().flush()

        user = provider.get_principal_bylogin('test')
        self.assertIsInstance(user, CrowdUser)
        self.assertEqual(user.login, 'test')

    def test_crowd_user_ctor(self):
        from ptahcrowd.provider import CrowdUser

        user = CrowdUser(name='user-name', login='user-login',
                         email='user-email', password='passwd')

        self.assertEqual(user.name, 'user-name')
        self.assertEqual(user.login, 'user-login')
        self.assertEqual(user.email, 'user-email')
        self.assertEqual(user.password, 'passwd')
        self.assertTrue(user.__uri__.startswith('ptah-crowd-user:'))
        self.assertEqual(str(user), 'user-name')
        self.assertEqual(repr(user), 'CrowdUser<%s:%s>'%(
            user.name, user.__uri__))

    def test_crowd_user_change_password(self):
        from ptahcrowd.provider import CrowdUser, change_password

        user = CrowdUser(name='user-name', login='user-login',
                         email='user-email', password='passwd')

        change_password(user, '123456')
        self.assertEqual(user.password, '123456')

    def test_crowd_user_change_search(self):
        from ptahcrowd.provider import CrowdUser, CrowdAuthProvider

        user = CrowdUser(name='user-name', login='user-login',
                         email='user-email', password='passwd')
        ptah.get_session().add(user)
        ptah.get_session().flush()
        uri = user.__uri__

        users = list(CrowdAuthProvider.search('user'))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].__uri__, uri)

        users = list(CrowdAuthProvider.search('email'))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].__uri__, uri)


class TestPasswordChanger(PtahTestCase):

    _includes = ('ptahcrowd',)

    def test_password_changer(self):
        from ptahcrowd.provider import CrowdUser

        user = CrowdUser(name='user-name', login='user-login',
                         email='user-email', password='passwd')

        self.assertTrue(ptah.pwd_tool.can_change_password(user))
