from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.wiki import api as wikiapi, formatter as wikiformatter

from genshi import builder

saved_format_link = None
def format_link(self, formatter, ns, pagename, label, ignore_missing, original_label=None):
    link = saved_format_link(self, formatter, ns, pagename, label, ignore_missing, original_label)

    if isinstance(link, builder.Element) and type(formatter) is wikiformatter.Formatter and link.tag == 'a' and 'missing' in link.attrib.get('class', ''):
        self.env.log.warning("Bad wiki link: %s, referenced from %s" % (pagename, formatter.req.path_info))

    return link

class BadLinks(Component):
    """This component logs bad local links found in wiki content."""
    
    implements(IEnvironmentSetupParticipant)

    def __init__(self):
        global saved_format_link
        if self.compmgr.enabled[self.__class__]:
            if saved_format_link is None:
                saved_format_link = wikiapi.WikiSystem._format_link
                wikiapi.WikiSystem._format_link = format_link

    def environment_created(self):
        """Called when a new Trac environment is created."""
        pass

    def environment_needs_upgrade(self, db):
        """Called when Trac checks whether the environment needs to be upgraded.
        
        Should return `True` if this participant needs an upgrade to be
        performed, `False` otherwise.
        
        """
        return False

    def upgrade_environment(self, db):
        """Actually perform an environment upgrade.
  
        Implementations of this method should not commit any database
        transactions. This is done implicitly after all participants have
        performed the upgrades they need without an error being raised.
        """
        pass
