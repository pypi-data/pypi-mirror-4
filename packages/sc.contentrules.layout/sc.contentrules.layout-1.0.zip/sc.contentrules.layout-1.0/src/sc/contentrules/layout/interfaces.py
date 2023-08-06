# -*- coding: utf-8 -*-

from zope.interface import Interface

from zope.schema import Choice
from sc.contentrules.layout import MessageFactory as _


class ISetLayoutAction(Interface):
    """ Configuration available for this content rule
    """
    layout = Choice(title=_(u"Layout"),
                    description=_(u"Select the layout to be applied to the "
                                  u"content item. If no Content Type condition"
                                  u" was created for this rule, only Default "
                                  u"View will be available. Also, if more than"
                                  u" one content type is selected in the "
                                  u" Type condition, an intersection of all "
                                  u"selected content type views will be "
                                  u"available to this action."),
                    required=True,
                    vocabulary='sc.contentrules.layout.available_views',)
