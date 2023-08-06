from trac.core import *
from trac.util.translation import _
from trac.web.api import IRequestFilter
from trac.web.chrome import add_notice

class GlobalRegisterOut(Component):
    """
    This component displays a notice to the user that accounts are shared globally on the server.
    """
    
    implements(IRequestFilter)

    # IRequestFilter methods
    
    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, content_type):
        return (template, content_type)

    def post_process_request(self, req, template, data, content_type):
        if template == "register.html":
            add_notice(req, _("Accounts registered here are shared with other systems on this server so maybe you already have an account registered. Try to login if it seems that your username is already taken."))
        return (template, data, content_type)
