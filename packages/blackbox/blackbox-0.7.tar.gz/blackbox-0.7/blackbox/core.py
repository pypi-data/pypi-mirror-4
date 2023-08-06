# blackbox IRC macros
#
# (c) slowpoke (Proxy) < proxypoke at lavabit dot com >
# Offical IRC channel: irc://irc.datnode.net/hacking
# Offical repository on github: https://github.com/proxypoke/blackbox_IRC-macros
#
# This program, hereafter called "blackbox", 
# is Free Software under the terms of the 
# GNU General Public license, which can be found at 
# http://www.gnu.org/copyleft/gpl.html.

'''blackbox.core - implements the basic IRC RFC commands as a usable base class

This module provides the base class for the other blackbox classes, such as
OperCore, IRC and Oper. It aims to fully implement the basic commands as
described in RFC 1459 (the IRC specification). It doesn't implement slightly
higher level commands, such as advanced channel privileges and other handy
stuff, but is nonetheless fully useable by itself.
'''

from __future__ import unicode_literals
from __future__ import print_function

import sys

import logging
import socket
import ssl

if sys.version_info[0] == 3:
    # XXX: pylint will complain about a broken import. Ignore it, it's correct.
    import queue
else:
    import Queue as queue



class IRCError(Exception):
    '''Exception for connection related errors. Really just a wrapper
    for the standard Exception.
    '''
    pass


class Core(object):

    '''This class implements all basic server commands as defined in the IRC
    RFC. It does not contain commands only usable by IRC Operators, these are
    contained in the OperCore class.
    '''

    def __init__(self, **kwargs):
        '''Initialize the object, create the socket, set the attributes to
        their default values. 

        Keyword Arguments:
            ssl -- Turn on ssl. Defaults to False.
            encoding -- Specify the encoding. Defaults to utf-8.
            pretend -- This puts blackbox into Pretend Mode.
                            Pretend Mode will cause blackbox to
                            be able to "pretend" as if it has connected
                            to a server and reroute everything that
                            would have been send to the server by send()
                            to the standard output. It's for testing
                            purposes.
                            Defaults to False.
        '''
        self._ssl = kwargs.get("ssl", False)
        self._encoding = kwargs.get("encoding", "utf-8")
        self._pretend = kwargs.get("pretend", False)
        
        self._buffer = queue.Queue()
        self.data = None
        self._socketOpen = False
        self._irc = None

        # set up loggers
        out = logging.getLogger("blackbox.out")
        out.addHandler(logging.NullHandler())
        _in = logging.getLogger("blackbox.in")
        _in.addHandler(logging.NullHandler())

        # Pretend Mode
        if self._pretend:
            self._isConnected = True
        else:
            self._isConnected = False

        # some book-keeping (might get extended in the future)
        self._nick = ""

    def _createSocket(self):
        '''(Re)create the internal socket.
        '''
        self._irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socketOpen = True
        if self._ssl:
            self._irc = ssl.wrap_socket(self._irc)

    @staticmethod
    def _addHashes(split):
        '''Adds hashes to a list of channels.
        '''
        channels = ""
        for channel in split:
            if channel != "":
                if channel[0] != '#':
                    channel = '#' + channel + ','
                    channels += channel
                else:
                    channels += channel + ','
        return channels


    def close(self):
        '''Close the socket, terminating the connection (if any).'''
        if self._socketOpen:
            self._irc.close()
            self._socketOpen = False

    def connect(self, host, port):
        '''Connect to a network with the given adress on the given port.

        Arguments:
            host -- the network's adress, either a DNS entry or an IP
            port -- the port on which the connection will run
        '''
        if not self._socketOpen:
            self._createSocket()
        if self._isConnected:
            raise IRCError("Already connected.")

        # convert types and abort on error
        host = str(host)
        try:
            port = int(port)
        except ValueError:
            raise TypeError("'port' parameter expects an integer. Got '{0}', "
                    "which is {1}.".format(port, type(port)))

        # initiate the connection
        self._irc.connect((host, port))
        self._isConnected = True

        
    def send(self, data):
        '''Send raw data to the IRC server, adding the trailing CRNL.

        Arguments:
            data -- a string describing a command to the server
        '''
        if not self._isConnected:
            raise IRCError("No active connection.")

        data = str(data)

        logging.getLogger("blackbox.out").info(data)
        
        # Pretend Mode
        if self._pretend:
            print(data)
            return

        # Add the trailing CRLF and send the encoded data
        data += "\r\n"
        self._irc.send(data.encode(self._encoding, 'replace'))


    def recv(self, bufferlen = 4096):
        '''Listen to data from the server, PONG if the server PINGs.
        Return the received data, one line at a time.

        Arguments:
            bufferlen -- Optional. Changes the size of the buffer.
                            Defaults to 4096.
        '''
        if not self._isConnected:
            raise IRCError("No active connection.")

        try:
            # let's see if there is data in the buffer
            data = self._buffer.get_nowait()
            return self._recvHelper(data)
        except queue.Empty:
            pass # go on and try to receive data

        tmpData = ''
        while True:
            data = self._irc.recv(bufferlen).decode(self._encoding, 'replace')

            # empty strings indicate a lost connection or some other problem
            # with the socket.
            if data == '':
                raise IRCError("Connection lost.")

            # get half-finished lines, if any
            data = tmpData + data
            tmpData = ''

            lines = data.split("\r\n")

            if lines[-1] != '':
                # oh no, an incomplete line!
                # store it for next time
                tmpData = lines.pop()
            else:
                # get rid of the empty string
                lines.pop()

            # put everything else in the buffer
            for line in lines:
                self._buffer.put(line)

            if tmpData == '':
                # we're not waiting for an incomplete line
                # let's get the hell out of here
                break


        data = self._buffer.get()
        return self._recvHelper(data)


    def _recvHelper(self, data):
        '''Helper function for recv().
        '''
        logging.getLogger("blackbox.in").info(data)

        # answer to pings
        if "PING" in data:
            self.send("PONG " + data.split()[1])

        # save to internal storage and return received data
        self.data = data
        return data



    def isConnected(self):
        '''Checks if blackbox is connected.

        Returns:

            True if connected, False otherwise.
        '''
        return bool(self._isConnected)


    def quit(self, quitmsg = ""):
        '''Quit the server. Optionally send a quit message.

        Arguments:
            quitmsg -- Optional. A quit message sent along the QUIT command.
        '''
        self.send("QUIT :{0}".format(quitmsg))
        self._isConnected = False


    def nickname(self, nick):
        '''Set or change the nickname.

        Arguments:
            nick -- a valid nickname (no spaces, special characters restricted)
        '''
        self._nick = nick
        self.send("NICK {0}".format(nick))

    def getnick(self):
        '''Returns the current nickname.'''
        return self._nick


    def username(self, user, real=None):
        '''Set the user- and realname.

        Arguments:
            user -- a valid username (no spaces, special characters restricted)
            real -- Optional. A real name or description (spaces allowed).
                    Defaults to the value of the user argument.
        '''
        if real == None:
            real = user
        self.send("USER {0} {0} {0} :{1}.".format(user, real))


    def join(self, channels, keywords = ""):
        '''Try to join a number of channels, with optional keywords.

        Arguments:
            channels -- the target channels, separated by ','
            keywords -- Optional. For channels with mode +k, separated by ','
        
        Note: When joining multiple channels with and without mode +k, either
        put the channels with +k first so their keywords get assigned correctly,
        or replace empty keywords with '*'. The first method is advised.
        '''
        channels = str(channels)
        # stop execution if the channel is an empty string
        if len(channels) == 0:
            return

        # split the channels string at every comma
        split = channels.split(',')

        # add the hash for every channel if it is missing
        channels = self._addHashes(split)

        # send join request to server
        self.send("JOIN {0} {1}".format(channels, keywords))


    def part(self, channels, partmsg = ""):
        '''Part one or more channels. Optionally send a part message.

        Arguments:
            channel -- the target channels, separated by ','
            partmsg -- Optional. A part message sent along with the PART command
        '''
        channels = str(channels)

        # stop execution if the channel is an empty string
        if len(channels) == 0:
            return

        # split the channels string at every comma
        split = channels.split(',')

        # add the hash for every channel if it is missing
        channels = self._addHashes(split)

        self.send("PART {0} :{1}".format(channels, partmsg))


    def say(self, target, msg):
        '''Send a message to a user or channel.

        Arguments:
            target -- either another user or channel (with the usual hash)
            msg -- the message to send
        '''
        self.send("PRIVMSG {0} :{1}".format(target, msg))


    def action(self, target, msg):
        ''''Do' an action in third person in a private message or channel.
            Has the same effect as '/me' in many clients.

        Arguments:
            target - either a user or channel (with the usual hash)
            msg - an action to 'do'. 
        '''
        self.send("PRIVMSG {0} :\x01ACTION {1}\x01".format(target, msg))


    def mode(self, target, mode, args = ""):
        '''Set the mode(s) of a channel or user, with optional arguments.

        Arguments:
            target -- the target channel or user
            mode -- one or more valid mode characters
            args -- Optional. One or more arguments (eg usernames).
        '''
        self.send("MODE {0} {1} {2}".format(target, mode, args))


    def kick(self, channel, user, reason = ""):
        '''Kick a user from a channel. 
        Usually requires privileges in that channel.

        Arguments:
            channel -- the target channel
            user -- the target user
            reason -- Optional. Specify a reason for the kick.
        '''
        self.send("KICK {0} {1} :{2}".format(channel, user, reason))


    def away(self, message = ""):
        '''Mark yourself as away, specifying a message to be sent to others. If 
        message is omitted, the away status will be removed.

        Arguments:
            message -- Message to be sent. Must be omitted to unmark
        '''
        self.send("AWAY {0}".format(message))


    def invite(self, user, channel):
        '''Invite a user to a channel.

        Arguments;
            user -- The user to invite
            channel -- The channel to invite to
        '''
        self.send("INVITE {0} {1}".format(user, channel))


    def notice(self, target, message):
        '''Send a notice to a user or channel.

        Arguments:
            target -- Either a user or a channel (prefixed with the usual hash)
            message -- The message to send
        '''
        self.send("NOTICE {0}, {1}".format(target, message))


    def serverpassword(self, password):
        '''Sends the server password (if required).

        Arguments:
            password -- The server password.
        '''
        self.send("PASS {0}".format(password))


    def settopic(self, channel, topic):
        '''Set the topic of a channel.
        Note: To query for the topic use gettopic().

        Arguments:
            channel -- The channel to set the topic for
            topic -- The text to set as the topic
        '''
        channel = str(channel)

        # stop execution if the channel is an empty string
        if len(channel) == 0:
            return

        # add the hash if it is missing
        if channel[0] != '#':
            channel = '#' + channel

        # Set the topic
        self.send("TOPIC {0} {1}".format(channel, topic))


    def admin(self, target = ""):
        '''Requests information about the administrator of the local server, or,
        if target is specified, the server of the target (wildcards accepted).

        Arguments:
            target -- Optional. Forward the request to the server of target
                (can be a client or a server)
        '''
        self.send("ADMIN {0}".format(target))


    def info(self, target = ""):
        '''Requests information about the local server, or, if target is
        specified, the server of the target (wildcards accepted).

        Arguments:
            target -- Optional. Forward the request to the server of target
                (can be a client or a server)
        '''
        self.send("INFO {0}".format(target))


    def ison(self, nicknames):
        '''Requests information about the online status of one or more 
        nicknames. The server returns all nicknames that are currently online.

        Arguments:
            nicknames -- Either a space separated string of nicknames, or a 
                python list of strings.
        '''
        # check type of kwarg
        if type(nicknames) == str:
            pass
        if type(nicknames) == list:
            nicknames = " ".join(nicknames)

        self.send("ISON {0}".format(nicknames))


    def links(self, servmask = "", server = ""):
        '''Queries the specified server, or, if omitted, the local server,
        for a list of known servers matching servmask. If servmask is omitted,
        all known servers are returned.

        Arguments:
            servmask -- Optional. Only servers matching servmask will be 
                returned. Accepts wildcards.
            server -- Optional. Queries the specified server instead of the 
                local server.
        '''
        self.send("LINKS {1} {0}".format(servmask, server))


    def chanlist(self, channels = "", server = ""):
        '''Queries for a list of channels and their topics. If channels is 
        specified, lists only the status of those channels. If server is 
        specified, forwards the request to that server.

        Arguments:
            channels - Optional. Requests only the listed channels, separated
                by ','
            server -- Optional. Forwards the request to the specified server.
                Accepts wildcards.
        '''
        channels = str(channels)


        # split the channels string at every comma
        split = channels.split(',')

        # add the hash for every channel if it is missing
        channels = self._addHashes(split)

        self.send("LIST {0} {1}".format(channels, server))

    def lusers(self, mask = "", server = ""):
        '''Gets statistics about the size of the IRC network. Without mask, the
        reply will be about the whole network, else about the parts that match
        mask. If server is omitted, the local server will be queried, else the
        query will be forwarded to server.

        Arguments:
            mask -- Optional. Narrows down the query, matching mask.
            server -- Optional. Forwards the query to server.
        '''
        self.send("LUSERS {0} {1}".format(mask, server))


    def names(self, channels = "", server = ""):
        '''Queries for a list of nicknames sorted by channel that are visible to
        the client. If channels is specified, only lists for those channels are
        returned. If server is given, the request is forwarded to that server.

        Arguments:
            channels - Optional. A list of channels separated by ','
            server -- Optional. Forwards the request to a server. Wildcards
                accepted.
        '''
        channels = str(channels)
        # stop execution if the channel is an empty string

        # split the channels string at every comma
        split = channels.split(',')

        # add the hash for every channel if it is missing
        channels = self._addHashes(split)

        self.send("NAMES {0} {1}".format(channels, server))


    def servlist(self, mask = "", type_ = ""):
        '''Lists services connected to the network and visible to the user, 
        matching mask if specified and of the matching type if specified.

        Arguments:
            mask -- Optional. Narrows down the matches. Wildcards accepted.
            type_ -- Optional. Only services matching type_ will be returned.
        '''
        self.send("SERVLIST {0} {1}".format(mask, type_))


    def stats(self, query, server = ""):
        '''Queries for certain server statistics. If note specified otherwise by
        the server argument, the local server is queried.

        Arguments:
            query -- A letter describing the query. Mostly implementation 
                dependant. The following SHOULD be supported by all servers:
                    l -- a list of the server's connections, their length and 
                        bandwidth usage
                    m -- usage count of all commands supported by the server
                    o -- a list of privileged users, operators
                    u -- server uptime
            server -- Optional. Forwards the request to a server. Wildcards
                accepted.
        '''
        self.send("STATS {0} {1}".format(query, server))


    def time(self, server = ""):
        '''Queries the local time of the local server, or a remote server if 
        specified.

        Arguments:
            server -- Optional. Forwards the request to a server. Wildcards
                accepted.
        '''
        self.send("TIME {0}".format(server))


    def gettopic(self, channel):
        '''Queries for the topic of a channel.
        Note: To set the topic of a channel use settopic().

        Arguments:
            channel -- The channel for which the topic is queried
        '''
        self.send("TOPIC {0}".format(channel))


    def trace(self, server = ""):
        '''Traces a route to the local or a remote server, if specified.

        Arguments:
            server --  Optional. Forwards the request to a server. Wildcards
                accepted.
        '''
        self.send("TRACE {0}".format(server))


    def userhost(self, nicknames):
        '''Queries for host information about the given nicknames.

        Arguments:
            nicknames -- A space separated string of nicknames or a python list
                of strings.
        '''
        # check the kwarg for type, replace if necessary
        if type(nicknames) == str:
            pass
        elif type(nicknames) == list:
            nicknames = " ".join(nicknames)

        self.send("USERHOST {0}".format(nicknames))

    def users(self, server = ""):
        '''Queries for a list of users logged into the server.
        Note: Disabled on most servers for security reasons.

        Arguments:
            server --  Optional. Forwards the request to a server. Wildcards
                accepted.
        '''
        self.send("USERS {0}".format(server))


    def version(self, server = ""):
        '''Queries for the version of the server program.

            server --  Optional. Forwards the request to a server. Wildcards
                accepted.
        '''
        self.send("VERSION {0}".format(server))


    def who(self, mask = "", oponly = False):
        '''Queries for a list of information about all users matching mask,
        or, if mask is omitted, all users who aren't invisible (mode +i). If
        oponly is True, only operators matching mask will be listed.

        Arguments:
            mask -- Optional. Narrows down the query. Wildcards accepted.
            oponly -- Optional. List only Operators. Defaults to False.
        '''
        if oponly:
            self.send("WHO {0} o".format(mask))
        else:
            self.send("WHO {0}".format(mask))


    def whois(self, nickname, server = ""):
        '''Queries for information about a specific user.

        Arguments:
            nickname -- The nickname to query.
            server -- Optional. Forwards the request to a server. Wildcards
                accepted.
        '''
        self.send("WHOIS {1} {0}".format(nickname, server))


    def whowas(self, nickname, count = "", server = ""):
        '''Queries for information about a nickname that no longer exists.

        Arguments:
            nickname -- The nickname to query
            count -- Optional. Limits the maximum amount of entries that are
                returned, if any.
            server -- Optional. Forwards the request to a server. Wildcards
                accepted.
        '''
        self.send("WHOWAS {0} {1} {2}".format(nickname, count, server))


# =============================== [ OPER CORE ] ===============================

class OperCore(Core):

    '''This class implements all basic server commands as defined in the IRC
    RFC, including the commands reserved for IRC Operators. If your
    application does not have or need these privileges, consider using the
    Core class instead.  

    WARNING: ALL COMMANDS ARE UNTESTED. USE AT OWN RISK!

    Methods implementing RFC commands for Opers defined in this class:
        servconnect(targetserv, port [, remoteserv])
        die()
        kill(client, comment)
        oper(username, password)
        rehash()
        restart()
        service(nick, distribution, type_, info)
        squit(server, comment)
        wallops(message)
    '''

    def __init__(self, **kwargs):
        '''Initializes the blackbox module. Pass on the keyword
        arguments. See Core for documentation.

        '''
        Core.__init__(self, **kwargs)
        

    def servconnect(self, targetserv, port, remoteserv = ""):
        '''Requests the server to try to establish a new connection to another
        server. 

        Arguments:
            targetserv -- Server to connect to
            port -- Port on which to connect
            remoteserv -- Optional. Pass on the CONNECT request to the remote
                remote server instead
        '''
        self.send("CONNECT {0} {1} {2}".format(targetserv, port, remoteserv))

    def die(self, password = ""):
        '''Shuts down the local server.

        Arguments:
            password -- Optional. Required on some IRCds, like Unreal.
        '''
        self.send("DIE {0}".format(password))

    def kill(self, user, reason):
        '''Terminates the connection of a client with the server network.

        Arguments:
            user -- The target of the KILL command
            reason -- The reason for the KILL.
        '''
        self.send("KILL {0} {1}".format(user, reason))


    def oper(self, username, password):
        '''Obtains Oper privileges.

        Arguments:
            username -- The username for the Oper privileges
            password -- The password for the username
        '''
        self.send("OPER {0} {1}".format(username, password))


    def rehash(self):
        '''Forces the local server to reprocess its configuration file.
        '''
        self.send("REHASH")


    def restart(self, password = ""):
        '''Forces the local server to restart itself.

        Arguments:
            password -- Optional. Required on some IRCds, like Unreal.
        '''
        self.send("RESTART {0}".format(password))


    def service(self, nick, distribution, info):
        '''Registers a new service.

        Arguments:
            nick -- Name of the service
            distribution -- Visibility of the service
            info -- Description of the service
        '''
        self.send("SERVICE {0} * {1} 0 0 :{2}".format(nick, distribution, info))


    def squit(self, server, comment):
        '''Disconnects a server link.

        Arguments:
            server -- The target server (can be remote)
            comment -- A reason for this action.
        '''
        self.send("SQUIT {0} :{1}".format(server, comment))


    def wallops(self, message):
        '''Sends a message to all users with mode +w set.
        '''
        self.send("WALLOPS {0}".format(message))
