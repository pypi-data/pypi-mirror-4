from zope.i18nmessageid import MessageFactory

  # -*- extra stuff goes here -*- 

# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

tagNavigatorMessageFactory = MessageFactory('Products.tagNavigator')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
