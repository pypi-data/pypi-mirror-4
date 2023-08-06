# cube's specific schema
_ = unicode

# pylint: disable-msg=E0611,F0401
from yams.buildobjs import EntityType, String, RichString

class Card(EntityType):
    """a card is a textual content used as documentation, reference, procedure reminder"""
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'users'),
        'delete': ('managers', 'owners'),
        'update': ('managers', 'owners',),
        }

    title    = String(required=True, fulltextindexed=True, maxsize=256)
    synopsis = String(fulltextindexed=True, maxsize=512,
                      description=_("an abstract for this card"))
    content  = RichString(fulltextindexed=True, internationalizable=True,
                          default_format='text/rest')
    wikiid = String(maxsize=64, indexed=True)
