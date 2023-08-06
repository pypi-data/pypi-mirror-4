from zope.interface import Interface, Attribute
from zope import schema
from zope.component.interfaces import IObjectEvent


class IAddNewUser(Interface):
    """Include a add new user link to the sharing tab.
    """


class IUserLocallyAdded(IObjectEvent):
    """Event notified when a user is locally added to an object via
    the 'add new user' link.
    """

    userid = schema.TextLine(title=u"User id of the created user.")

    data = schema.List(title=u"Data associated to userid on object.")


class IAddUserSchemaExtender(Interface):
    """Add extra field to add user form.
    """
    order = Attribute(u"Order of the fields set in the form.")

    def add_fields(fields):
        """Add fields to the form.
        Return modified fields.
        """

    def handle_data(data, context, request):
        """Handle sent data.
        """
