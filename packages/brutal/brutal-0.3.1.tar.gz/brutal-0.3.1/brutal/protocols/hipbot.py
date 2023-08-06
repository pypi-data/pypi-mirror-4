import datetime
from twisted.application import service
from twisted.python import log
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
#from twisted.words.
from wokkel import muc
from wokkel import xmppim
from wokkel.client import XMPPClient


class Hipbot(muc.MUCClient):
    def __init__(self, server, room, nick):
        super(Hipbot, self).__init__()
        self.server = server
        self.room = room
        self.nick = nick
        self.room_jid = jid.internJID(self.room + '@' + self.server) # + '/' + self.nick)
        self.last = {}
        self.activity = None

    def connectionInitialized(self):
        def joinedRoom(room):
            print 'ROOM: {0!r}'.format(room.__dict__)
            if room.locked:
                return self.configure(room.roomJID, {})

        super(Hipbot, self).connectionInitialized()

        d = self.join(self.room_jid, self.nick)
        d.addCallback(joinedRoom)
        #d.addCallback(lambda _: log.msg("joined room"))
        d.addErrback(log.err, 'Join failed')

        print 'NICK: {0!r}'.format(self.nick)

    def receivedGroupChat(self, room, user, message):
        if message.body.startswith(self.nick + u':'):
            nick, text = message.body.split(':', 1)
            text = text.strip().lower()
            if text == 'sup':
                body = u'{0}: derp'.format(user.nick)
                self.groupChat(self.room_jid, body)

                #new msg to user

                #self.send()


#
#    def _gestLast(self, nick):
#        return self.last.get(nick.lower())
#
#    def _setLast(self, user):
#        user.last = datetime.datetime.now()
#        self.last[user.nick.lower()] = user
#        self.activity = user
#
#    def initialized(self):
#        self.join(self.server, self.room, self.nick).addCallback(self.initRoom)
#
#    @defer.inlineCallbacks
#    def initRoom(self, room):
#        if int(room.status) == muc.STATUS_CODE.ROOM_CREATED:
#            config_from = yield self.getConfiguration()


#openfire server: corey@qr7.com  admin / aids

from twisted.internet.task import LoopingCall
from wokkel.subprotocols import XMPPHandler


class HipchatClientKeepalive(XMPPHandler):
    interval = 15
    lc = None

    def space(self):
        #print '*** SENDING KEEPALIVE ***'
        self.xmlstream.send(' ')

    def connectionInitialized(self):
        self.lc = LoopingCall(self.space)
        self.lc.start(self.interval)

    def connectionLost(self, reason):
        if self.lc:
            self.lc.stop()


# channel join
#2013-02-15 22:23:28-0800 [XmlStream,client] RECV: 'presence to="bot@lolwat/882cea13" from="testing@conference.lolwat/Corey"><c xmlns="http://jabber.org/protocol/caps" node="http://pidgin.im/" hash="sha-1" ver="DdnydQG7RGhP9E3k9Sf+b+bF0zo="/><x xmlns="http://jabber.org/protocol/muc#user"><item affiliation="none" role="participant"/></x></presence>'
# channel leave
#2013-02-15 22:18:56-0800 [XmlStream,client] RECV: 'presence to="bot@lolwat/882cea13" from="testing@conference.lolwat/Corey" type="unavailable"><c xmlns="http://jabber.org/protocol/caps" node="http://pidgin.im/" hash="sha-1" ver="DdnydQG7RGhP9E3k9Sf+b+bF0zo="/><x xmlns="vcard-temp:x:update"><photo>6b7af5f2e83ddc2e8625932869b04f26ce0b5a41</photo></x><x xmlns="http://jabber.org/protocol/muc#user"><item affiliation="none" role="none"/></x></presence>'
# channel msg
#2013-02-15 22:25:53-0800 [XmlStream,client] RECV: 'message type="groupchat" id="purple4dfa975" to="bot@lolwat/882cea13" from="testing@conference.lolwat/Corey"><body>WAT</body></message>'


if __name__ == '__main__':

    import sys
    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout, setStdout=0)

    bot_jid = jid.internJID('bot@lolwat')
    client = XMPPClient(bot_jid, 'aids', host='localhost')
    client.logTraffic = True

    client.startService()
    #client.setServiceParent(application)

    presence = xmppim.PresenceClientProtocol()
    presence.setHandlerParent(client)
    presence.available()



    keepalive = HipchatClientKeepalive()
    keepalive.setHandlerParent(client)


    #muc_handler = Hipbot('conf.hipchat.com', '25234_bottes', 'CORE dump')
    muc_handler = Hipbot('conference.lolwat', 'testing', 'bot')
    # 2013-02-14 17:31:39-0800 [XmlStream,client] RECV: '<'
    # 2013-02-14 17:31:39-0800 [XmlStream,client] RECV: 'message type="groupchat" id="purple1a4a9083" to="bot@lolwat/5f7bfd8a" from="testing@conference.lolwat/Corey"><body>bot: sup</body></message>'
    # 2013-02-14 17:31:39-0800 [XmlStream,client] SEND: "<message to='testing@conference.lolwat/bot' type='groupchat'><body>Corey: derp</body></message>"
    # 2013-02-14 17:31:39-0800 [XmlStream,client] RECV: '<'
    # 2013-02-14 17:31:39-0800 [XmlStream,client] RECV: 'message to="bot@lolwat/5f7bfd8a" type="error" from="testing@conference.lolwat/bot"><body>Corey: derp</body><error code="400" type="modify"><bad-request xmlns="urn:ietf:params:xml:ns:xmpp-stanzas"/></error></message>'
    muc_handler.setHandlerParent(client)

    reactor.run()
else:

    application = service.Application('dat muc client')

    #client = XMPPClient(jid.internJID('25234_202838@chat.hipchat.com/COREbot'), 'N^13jGqg$T7J')
    #client = XMPPClient(jid.internJID('bot@localhost/bot'), 'aids', 'localhost')
    bot_jid = jid.internJID('bot@lolwat')
    client = XMPPClient(bot_jid, 'aids', host='localhost')

    client.logTraffic = True

    client.setServiceParent(application)

    presence = xmppim.PresenceClientProtocol()
    presence.setHandlerParent(client)
    presence.available()

    keepalive = HipchatClientKeepalive()
    keepalive.setHandlerParent(client)


    #muc_handler = Hipbot('conf.hipchat.com', '25234_bottes', 'CORE dump')
    muc_handler = Hipbot('conference.lolwat', 'testing', 'bot')
    # 2013-02-14 17:31:39-0800 [XmlStream,client] RECV: '<'
    # 2013-02-14 17:31:39-0800 [XmlStream,client] RECV: 'message type="groupchat" id="purple1a4a9083" to="bot@lolwat/5f7bfd8a" from="testing@conference.lolwat/Corey"><body>bot: sup</body></message>'
    # 2013-02-14 17:31:39-0800 [XmlStream,client] SEND: "<message to='testing@conference.lolwat/bot' type='groupchat'><body>Corey: derp</body></message>"
    # 2013-02-14 17:31:39-0800 [XmlStream,client] RECV: '<'
    # 2013-02-14 17:31:39-0800 [XmlStream,client] RECV: 'message to="bot@lolwat/5f7bfd8a" type="error" from="testing@conference.lolwat/bot"><body>Corey: derp</body><error code="400" type="modify"><bad-request xmlns="urn:ietf:params:xml:ns:xmpp-stanzas"/></error></message>'
    muc_handler.setHandlerParent(client)