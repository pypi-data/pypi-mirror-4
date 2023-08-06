import re

from postmonkey import PostMonkey

from zope import schema
from zope.interface import Interface
from zope.interface import invariant
from zope.interface import Invalid
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.mailchimp import _

available_fields = SimpleVocabulary([
    SimpleTerm(value=u'subscriber_list', title=_(u'Subscriber list')),
    SimpleTerm(value=u'email', title=_(u'E-Mail'))
])


class ICollectiveMailchimp(Interface):
    """Marker interface that defines a ZTK browser layer. We can reference
    this in the 'layer' attribute of ZCML <browser:* /> directives to ensure
    the relevant registration only takes effect when this theme is installed.

    The browser layer is installed via the browserlayer.xml GenericSetup
    import step.
    """


class NotAnEmailAddress(schema.ValidationError):
    __doc__ = _(u"Invalid email address")


check_email = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+.)*[a-zA-Z]{2,4}")\
    .match


def validate_email(value):
    if not check_email(value):
        raise NotAnEmailAddress(value)
    return True


class INewsletterSubscribe(Interface):

    email = schema.TextLine(
        title=_(u"Email address"),
        description=_(
            u"help_email",
            default=u"Please enter your email address."
        ),
        required=True,
        constraint=validate_email)

    interest_groups = schema.Tuple(
        title=_(u"Interest groups"),
        description=_(
            u"help_interest_groups",
            default=u""
        ),
        value_type=schema.Choice(
            vocabulary="collective.mailchimp.vocabularies.InterestGroups",
        ),
        required=False,
    )

    email_type = schema.Choice(
        title=_(u"Mail format"),
        vocabulary="collective.mailchimp.vocabularies.EmailType",
        default="text",
        required=False,
    )

    list_id = schema.TextLine(
        title=_(u"List ID"),
        required=False
    )


class IMailchimpLocator(Interface):
    """
    """


class IMailchimpSettings(Interface):
    """Global mailchimp settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    api_key = schema.TextLine(
        title=_(u"MailChimp API Key"),
        description=_(
            u"help_api_key",
            default=u"Enter in your MailChimp key here (.e.g. " +
                    u"'8b785dcabe4b5aa24ef84201ea7dcded-us4'). Log into " +
                    u"mailchimp.com, go to account -> extras -> API Keys & " +
                    u"Authorized Apps and copy the API Key to this field."
        ),
        default=u"",
        required=True
    )

    email_type = schema.Choice(
        title=_(u"email_type"),
        description=_(
            u"help_email_type",
            default=u"Email type preference for the email (html, text, or "
                    u"mobile defaults to html)"),
        vocabulary="collective.mailchimp.vocabularies.EmailType",
        default="text",
        required=True,
    )

    email_type_is_optional = schema.Bool(
        title=_(u"email_type_is_optional"),
        description=_(
            u"help_email_type_is_optional",
            default=u"Let users choose their email type preference in the "
                    u"newsletter subscription form."
        ),
        required=True,
        default=False
    )

    default_list = schema.Choice(
        title=_(u"default_list"),
        description=_(
            u"help_default_list",
            default=u"Default list which is used in the @@newsletter view if "
                    u"no list_id param is provided."),
        vocabulary="collective.mailchimp.vocabularies.AvailableLists",
        required=False,
    )

    double_optin = schema.Bool(
        title=_(u"double_optin"),
        description=_(
            u"help_double_optin",
            default=u"Flag to control whether a double opt-in confirmation "
                    u"message is sent, defaults to true. Abusing this may "
                    u"cause your account to be suspended."
        ),
        required=True,
        default=True
    )

    update_existing = schema.Bool(
        title=_(u"update_existing"),
        description=_(
            u"help_update_existing",
            default=u"Flag to control whether existing subscribers should be "
                    u"updated instead of throwing an error, defaults to false"
        ),
        required=True,
        default=False
    )

    replace_interests = schema.Bool(
        title=_(u"replace_interests"),
        description=_(
            u"help_replace_interests",
            default=u"Flag to determine whether we replace the interest "
                    u"groups with the groups provided or we add the provided"
                    u"groups to the member's interest groups (optional, "
                    u"defaults to true)"
        ),
        required=True,
        default=True
    )

    send_welcome = schema.Bool(
        title=_(u"send_welcome"),
        description=_(
            u"help_send_welcome",
            default=u"If your double_optin is false and this is true, we "
                    u"will send your lists Welcome Email if this subscribe "
                    u"succeeds - this will *not* fire if we end up updating "
                    u"an existing subscriber. If double_optin is true, this "
                    u"has no effect. defaults to false."
        ),
        required=True,
        default=False
    )

    @invariant
    def valid_api_key(data):
        if len(data.api_key) == 0:
            return
        mailchimp = PostMonkey(data.api_key)
        try:
            return mailchimp.ping()
        except:
            raise Invalid(
                u"Your MailChimp API key is not valid. Please go " +
                u"to mailchimp.com and check your API key.")
