#!/usr/bin/env python

#
#  Phoenix Emulator MUS Interface 0.9
#  https://pypi.python.org/pypi/phoenix
#
#  A full-featured interface for the Phoenix MUS server.
#
#  Copyright (c) 2013 Bui, <bui@bui.pm>.
#  Released under the MIT License.
#

import socket
import time


class Phoenix(object):
    def __init__(self, addr, port):
        """Creates a Phoenix object, representing a Phoenix MUS session."""
        self.addr = addr
        self.port = port
        self.connected = False
        self.reconnect = True
        self.send_timeout = 3

    def alert(self, user_id, message):
        """Sends an alert message to the given user ID."""
        self._send_command('alert', str(user_id) + ' ' + message)

    def execute_sql(self, query):
        """Executes an SQL query in the database."""
        self._send_command('exe', query)

    def give_item(self, user_id, item_id, page_id, gift_message=''):
        """Sends an item as a gift to the given user ID."""
        self._send_command('giveitem', '%s %s %s %s' %
                           (str(user_id), str(item_id), str(page_id), gift_message))

    def hotel_alert(self, message, link=None):
        """Sends an alert message to all online users."""
        if link:
            self._send_command('hal', link + ' ' + message)
        else:
            self._send_command('ha', message)

    def room_alert(self, room_id, message):
        """Sends an alert message to everyone in the given room ID."""
        self._send_command('roomalert', room_id + ' ' + message)

    def shutdown(self):
        """Safely shuts down the server."""
        try:
            self._send_command('shutdown')
        except PhoenixError, e:
            if '[Errno 10054]' in str(e):
                pass
            else:
                raise

    def send_user(self, user_id, room_id):
        """Sends the given user ID to the given room ID."""
        self._send_command('senduser', str(user_id) + ' ' + str(room_id))

    def signout(self, user_id):
        """Ends the session of the given user ID."""
        self._send_command('signout', str(user_id))

    def staff_alert(self, message):
        """Sends an alert message to all online staff members."""
        self._send_command('sa', message)

    def unload_room(self, room_id):
        """Removes all the users from the given room ID."""
        self._send_command('unloadroom', str(room_id))

    def update_bans(self):
        """Updates the bans table."""
        self._send_command('reloadbans')

    def update_bots(self):
        """Updates the bots table."""
        self._send_command('update_bots')

    def update_catalogue(self):
        """Updates the catalogue table."""
        self._send_command('update_catalogue')

    def update_credits(self, user_id):
        """Updates the amount of credits of the given user ID."""
        self._send_command('updatecredits', str(user_id))

    def update_filter(self):
        """Updates the word filter."""
        self._send_command('update_filter')

    def update_items(self):
        """Updates the furniture table."""
        self._send_command('update_items')

    def update_group(self, group_id):
        """Updates the database entry of the given group ID."""
        self._send_command('updategroup', str(group_id))

    def update_look(self, user_id):
        """Updates the look of the given user ID."""
        self._send_command('updatelook', str(user_id))

    def update_motto(self, user_id):
        """Updates the motto of the given group ID."""
        self._send_command('updatemotto', str(user_id))

    def update_pixels(self, user_id):
        """Updates the amount of pixels of the given user ID."""
        self._send_command('updatepixels', str(user_id))

    def update_points(self, user_id):
        """Updates the amount of points of the given user ID."""
        self._send_command('updatepoints', str(user_id))

    def update_settings(self):
        """Updates the server_settings table."""
        self._send_command('updatesettings')

    def update_user_groups(self, user_id):
        """Updates the groups of the given user ID."""
        self._send_command('updateusersgroups', str(user_id))

    def update_user_rooms(self, user_id):
        """Updates the rooms of the given user ID."""
        self._send_command('updateusersrooms', str(user_id))

    def update_vip(self, user_id):
        """Updates the VIP status the given user ID."""
        self._send_command('updatevip', str(user_id))

    def _send_command(self, command, payload=''):
        """Sends a command to the MUS server."""
        if not self.connected:
            if self.reconnect:
                self._try_connect()
            else:
                raise PhoenixError('There is no established connection.')

        try:
            sent_at = int(time.time())
            self.sock.send(command + '\x01' + payload)

            while int(time.time()) <= sent_at + int(self.send_timeout):
                res = self.sock.recv(64)
                if res == '@AHello Housekeeping, Love from Phoenix Emu\x01':
                    return

            self.connected = False
            if self.reconnect:
                self._try_connect()
            else:
                raise PhoenixError('There is no established connection.')

        except socket.error, e:
            for en in ['[Errno 10057]', '[Errno 10053]']:
                if en in str(e):
                    self.connected = False
                    if self.reconnect:
                        self._try_connect()
                        self._send_command(command, payload)
                        return
                    else:
                        raise PhoenixError('There is no established connection.')

            raise PhoenixError(str(e))

    def _try_connect(self):
        """Attempts to connect to the MUS server using a socket."""
        if self.connected:
            self.sock.close()

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.addr, self.port))
            self.connected = True
        except socket.error, e:
            if '[Errno 10061]' in str(e):
                raise PhoenixError('The remote server refused the connection.')
            else:
                raise PhoenixError(str(e))


class PhoenixError(Exception):
    pass
