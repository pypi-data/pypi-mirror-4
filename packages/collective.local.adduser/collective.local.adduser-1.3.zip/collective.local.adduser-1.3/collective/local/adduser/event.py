from zope.component.interfaces import ObjectEvent
from zope.interface import implements

from collective.local.adduser.interfaces import IUserLocallyAdded


class UserLocallyAdded(ObjectEvent):
    implements(IUserLocallyAdded)

    def __init__(self, object, userid, data):
        self.object = object
        self.userid = userid
        self.data = data
