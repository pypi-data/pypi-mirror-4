"""
This is the main notifier service.

The design philisophy here is to send notification for "heads-up" events, 
that is events that MAY require a reaction from its recipient.

Emails are sent for "actionnable" events, that is events that require an action
to be taken (accept in a network or community, ...).
"""
from django.utils.translation import ugettext as _

from twistranet.twistapp.signals import *
import handlers


#                                       #
#           Account signals             #
#                                       #
invite_user.connect(
    handlers.MailHandler(
        recipient_arg = "target",
        text_template = "email/invite_user.txt",
        html_template = "email/invite_user.html",
    ),
    weak = False,
)

reset_password.connect(
    handlers.MailHandler(
        recipient_arg = "target",
        text_template = "email/reset_password.txt",
        html_template = "email/reset_password.html",
    ),
    weak = False,
)

content_created.connect(
    handlers.MailHandler(
        recipient_arg = "target",
        text_template = "email/created_content.txt",
        html_template = "email/created_content.html",
    ),
    weak = False,
)

#                                       #
#           Community signals           #
#                                       #
join_community.connect(
    handlers.NotificationHandler(
        owner_arg = "client",
        publisher_arg = "community",
        message = _(u"""%(client)s joined %(community)s."""),
    ),
    weak = False,
)

invite_community.connect(
    handlers.NotificationHandler(
        owner_arg = "target",
        publisher_arg = "target",
        permissions = "private",
        message = _(u"""You are invited in %(community)s community"""),
    ),
    weak = False,
)

#                                       #
#           Network Signals             #
#                                       #
request_add_to_network.connect(
    handlers.NotificationHandler(
        owner_arg = "target",
        publisher_arg = "target",
        message = _(u"""%(client)s wants to add you to his/her network."""),
        permissions = "private",
    ),
    weak = False,
)

request_add_to_network.connect(
    handlers.MailHandler(
        recipient_arg = "target",
        text_template = "email/request_add_to_network.txt",
        html_template = "email/request_add_to_network.html",
    ),
    weak = False,
)

accept_in_network.connect(
    handlers.NotificationHandler(
        owner_arg = "client",
        publisher_arg = "target",
        message = _(u"""%(client)s is now connected to %(target)s."""),
    ),
    weak = False,
)

