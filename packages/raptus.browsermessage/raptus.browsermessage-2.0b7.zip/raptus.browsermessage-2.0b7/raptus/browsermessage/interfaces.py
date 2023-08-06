from zope import interface, schema

from raptus.browsermessage import _

UNKNOWN = 'unknown'


class IBrowserDetection(interface.Interface):
    """ Detects browser versions and platforms
    """

    def platform():
        """ Returns the platform
        """

    def browser():
        """ Returns the browser
        """

    def version():
        """ Returns the browser version
        """

    def check(condition):
        """ Returns whether the condition matches or not
        """


class IBrowserCondition(interface.Interface):
    """ A browser
    """

    platform = schema.Set(
        title=_(u'Platform'),
        required=False,
        value_type=schema.Choice(
            vocabulary=schema.vocabulary.SimpleVocabulary([
                schema.vocabulary.SimpleTerm('win', 'win', u'Windows'),
                schema.vocabulary.SimpleTerm('mac', 'mac', u'Mac'),
                schema.vocabulary.SimpleTerm('linux', 'linux', u'Linux'),
            ])
        )
    )

    browser = schema.Choice(
        title=_(u'Browser'),
        required=True,
        vocabulary=schema.vocabulary.SimpleVocabulary([
            schema.vocabulary.SimpleTerm('ie', 'ie', u'Internet Explorer'),
            schema.vocabulary.SimpleTerm('firefox', 'firefox', u'Firefox'),
            schema.vocabulary.SimpleTerm('chrome', 'chrome', u'Chrome'),
            schema.vocabulary.SimpleTerm('safari', 'safari', u'Safari'),
            schema.vocabulary.SimpleTerm('opera', 'opera', u'Opera'),
            schema.vocabulary.SimpleTerm(UNKNOWN, 'other', u'Other')
        ])
    )

    version_min = schema.Int(
        title=_(u'Version minimum'),
        required=False
    )

    version_max = schema.Int(
        title=_(u'Version maximum'),
        required=False
    )

    def __str__():
        """ Converts the condition to a string
        """

    def from_str(string):
        """ Creates a condition from a string
        """


class IBrowserConditions(interface.Interface):
    """ Stores and provides browser conditions
    """

    def add(condition):
        """ Adds a new condition
        """

    def clear():
        """ Removes all conditions
        """

    def __iter__():
        """ Iterator over the available conditions
        """


class IBrowserConditionsForm(interface.Interface):
    """ A set of browser conditions
    """

    conditions = schema.List(
        title=_(u'Browsers for which the message appears'),
        description=_(u'Select the Browsers for which the upgrade message shall appear'),
        value_type=schema.Object(
            schema=IBrowserCondition
        )
    )

    proposals = schema.Set(
        title=_(u'Browsers to suggest'),
        description=_(u'Select the Browsers to present to the user for upgrade'),
        required=True,
        value_type=schema.Choice(
            vocabulary='raptus.browsermessage.proposals'
        )
    )
