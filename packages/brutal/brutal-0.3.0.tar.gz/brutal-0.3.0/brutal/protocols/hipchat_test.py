from xmpp import XmppBackend


class HipchatBackend(XmppBackend):
    def configure(self, *args, **kwargs):
        super(HipchatBackend, self).configure(*args, **kwargs)

        self.mention_name = kwargs.get('mention_name')
