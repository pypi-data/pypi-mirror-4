# python-boxcar
#
# Copyright (C) 2013 Mark Caudill
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import requests
from boxcar.exc import (BoxcarError, UserNotSubscribed,
                        UserAlreadySubscribed, UserDoesNotExist)
import random


class Provider(object):
    '''An API to Boxcar.io.'''

    def __init__(self, key=None, secret=None,
                 base='https://boxcar.io/devices/providers/'):
        '''
        Initialize.

        :param key: the API key
        :type  key: str
        :param secret: the API secret key
        :type  secret: str
        :param base: the base URI for the API - modify at your own risk
        :type  base: str
        '''
        self.key = key
        self.secret = secret
        self._base = base

    def subscribe(self, email=None):
        '''
        Subscribe a user to this service (actually sends them a request).

        :param email: the user's email address to add
        :type  email: str
        '''
        url = '%s%s/notifications/subscribe' % (self._base, self.key)
        data = {'email': email}
        response = requests.post(url=url, data=data)
        if response.status_code == 404:
            raise UserDoesNotExist
        elif response.status_code == 401:
            raise UserAlreadySubscribed

    def notify(
            self, emails=None, from_screen_name=None, message=None,
            from_remote_service_id=None, source_url=None, icon_url=None):
        '''
        Send a notification to one or more users.

        :param emails: the list of email addresses for users to notify
        :type  emails: list of strs
        :param from_screen_name: the user or application sending the message
        :type  from_screen_name: str
        :param message: the message to display to the user
        :type  message: str
        :param from_remote_service_id: a unique ID to help prevent duplicates
                                       will be randomly generated if not
                                       specified
        :type  from_remote_service_id: int
        :param source_url: optional URL for user to go to for more info
        :type  source_url: str
        :param icon_url: optional icon to display with message
        :type  icon_url: str
        '''
        url = '%s%s/notifications' % (self._base, self.key)
        data = {
            'emails': emails,
            'notification[from_screen_name]': from_screen_name,
            'notification[message]': message}
        if not from_remote_service_id:
            data['notification[from_remote_service_id]'] = \
                    random.randint(0, 4294967295)
        if source_url:
            data['notification[source_url]'] = source_url
        if icon_url:
            data['notification[icon_url]'] = icon_url
        response = requests.post(url=url, data=data)
        if response.status_code == 401:
            raise UserNotSubscribed
        elif response.status_code == 404:
            raise UserDoesNotExist

    def broadcast(
            self, from_screen_name=None, message=None,
            from_remote_service_id=None, source_url=None, icon_url=None):
        '''
        Broadcast to all services.

        :param from_screen_name: the user or application sending the message
        :type  from_screen_name: str
        :param message: the message to display to the user
        :type  message: str
        :param from_remote_service_id: a unique ID to help prevent duplicates
        :type  from_remote_service_id: int
        :param source_url: optional URL for user to go to for more info
        :type  source_url: str
        :param icon_url: optional icon to display with message
        :type  icon_url: str
        '''
        url = '%s%s/notifications/broadcast' % (self._base, self.key)
        data = {
            'secret': self.secret,
            'notification[from_screen_name]': from_screen_name,
            'notification[message]': message}
        if not from_remote_service_id:
            data['notification[from_remote_service_id]'] = \
                    random.randint(0, 4294967295)
        if source_url:
            data['notification[source_url]'] = source_url
        if icon_url:
            data['notification[icon_url]'] = icon_url
        response = requests.post(url=url, data=data)
        if response.status_code != 200:
            raise BoxcarError('Unknown error.')
