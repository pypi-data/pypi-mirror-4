from trac.core import *
from trac.env import IEnvironmentSetupParticipant
import trac.ticket.web_ui as ticketwebui

saved_toggle_cc = None
def toggle_cc(self, req, cc):
    email = req.session.get('email')
    if req.authname != 'anonymous' and req.session.has_key('email'):
        del req.session['email']
    res = saved_toggle_cc(self, req, cc)
    if email:
        req.session['email'] = email
    return res

class UsernameCC(Component):
    """This component modifies Trac to prefer username to email address in ticket CC checkbox."""
    
    implements(IEnvironmentSetupParticipant)

    def __init__(self):
        global saved_toggle_cc
        if self.compmgr.enabled[self.__class__]:
            if saved_toggle_cc is None:
                saved_toggle_cc = ticketwebui.TicketModule._toggle_cc
                ticketwebui.TicketModule._toggle_cc = toggle_cc

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
