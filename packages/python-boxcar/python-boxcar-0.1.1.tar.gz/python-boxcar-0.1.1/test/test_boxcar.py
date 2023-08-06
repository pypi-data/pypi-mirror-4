import unittest
import boxcar
from boxcar import Provider


class Test(unittest.TestCase):
    '''Unit tests for boxcar.'''

    def setUp(self):
        self.provider = Provider(
                key='vKLoSqB4vhQ4BPZ2TQ4z',
                secret='hPiCqQMuRCDXbkVXYsq4zOu5AGZEZ0bGye7dfl5b')

    def test_provider(self):
        self.assertIsInstance(self.provider, Provider)

    def test_provider_subscribe(self):
        self.assertRaises(
                boxcar.exc.UserAlreadySubscribed,
                self.provider.subscribe,
                email='mark@markcaudill.me')
        self.assertRaises(
                boxcar.exc.UserDoesNotExist,
                self.provider.subscribe,
                email='foo@markcaudill.me')

    def test_provider_notify(self):
        self.assertRaises(
                boxcar.exc.UserNotSubscribed,
                self.provider.notify,
                emails=['markcaudill@gmail.com'],
                from_screen_name='unittest',
                message='This is a test message from unittest.',
                source_url='https://github.com/markcaudill/boxcar',
                icon_url='http://i.imgur.com/RC220wK.png')
        self.provider.notify(
            emails=['mark@markcaudill.me'],
            from_screen_name='unittest',
            message='This is a test message from unittest.',
            source_url='https://github.com/markcaudill/boxcar',
            icon_url='http://i.imgur.com/RC220wK.png')

    @unittest.skip('This test will only succeed using a non-generic provider. It is not safe to pass around keys to non-generic providers for a variety of reasons.')
    def test_provider_broadcast(self):
        self.provider.broadcast(
            from_screen_name='unittest',
            message='This is a test broadcast from unittest.',
            source_url='https://github.com/markcaudill/boxcar',
            icon_url='http://i.imgur.com/RC220wK.png')


if __name__ == '__main__':
    unittest.main()
