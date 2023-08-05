from zope import schema
from zope.interface import Interface


class IShoppinglist(Interface):
    """ A shoppinglist can hold UIDs of objects from the site
    """

    uids = schema.List(
        title=u'Items',
        description=u'Select the items you want to remove from the ' \
                    'shoppinglist',
        required=False,
        value_type=schema.TextLine(),
        default=[],
    )

    clearList = schema.Bool(
        title=u'Clear entire shoppinglist',
        description=u'If you want to remove all items, ' \
                     'tick this box and click the "Clear" button',
        required=False,
        default=False,
    )


class IAddToShoppinglist(Interface):
    """ An interface that lets you add content to a shoppinglist
    """
