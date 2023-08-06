from zope.interface import Interface
from zope import schema
from rt.simpleslider import MessageFactory as _


class ISliderUtils(Interface):
    """ Interface that provides slider utils """

    def show_slider():
        """ """


class ISliderSource(Interface):
    """ Interface that provides slider source """

    def getSliderImages():
        """ returns generator """

    def getCaption():
        """ """

    def getImage():
        """ """

    def items():
        """ """


class IBrowserLayer(Interface):
    """ Marker interface when this add-on is installed """


class ISliderBrain(Interface):
    """ Marker interface for slider brain wrapper """


class ISliderSettings(Interface):

        simpleslider_allowed_types = schema.Tuple(
                          title=_(u"Portal types for 'simpleslider' field"),
                          description=_(u"Portal types 'simpleslider' field may be attached to."),
                          default=tuple(),
                          value_type=schema.Choice(vocabulary="plone.app.vocabularies.UserFriendlyTypes"),
                          required=False
                          )
