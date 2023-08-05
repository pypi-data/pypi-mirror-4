from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from persistent.list import PersistentList

META_TYPE = 'MockMailHost'

class MockMailHost(SimpleItem):
    """ Testable Emailer """

    meta_type = META_TYPE

    index_html = None

    def __init__(self):
        """Initialize a new MailHost instance """
        self.messages = PersistentList()

    def send(self, msg, *args, **kwargs):
        """ store the mail """
        self.messages.append(msg)

    def reset(self):
        """ resets messages """
        self.messages = PersistentList()

    secureSend = send

InitializeClass(MockMailHost)
