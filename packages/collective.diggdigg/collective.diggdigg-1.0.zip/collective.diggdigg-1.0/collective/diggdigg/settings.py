from zope import interface
from zope import schema


class Settings(interface.Interface):
    """addon settings"""

    buttons = schema.List(title=u"Buttons",
              value_type=schema.Choice(title=u"Button",
                        vocabulary="collective.diggdigg.vocabulary.buttons"),
              default=["twitter", "facebook", "plusone", "linkedin"]
              )

    filter_types = schema.List(title=u"Filter types",
              value_type=schema.Choice(title=u"Content type",
                vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"),
              default=['Document', 'Blog Entry', 'Event', 'NewsItem']
              )
