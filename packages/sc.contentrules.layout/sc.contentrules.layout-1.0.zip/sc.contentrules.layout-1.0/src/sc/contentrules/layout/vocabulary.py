# -*- coding: utf-8 -*-
from Acquisition import aq_parent
import logging

from zope.browsermenu.interfaces import IBrowserMenu

from zope.component import getUtility
from zope.component import queryMultiAdapter

from zope.interface import implements
from zope.interface import Interface

from zope.schema.interfaces import IVocabularyFactory

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName

from plone.contentrules.rule.interfaces import IRule
from plone.app.contentrules.conditions.portaltype import IPortalTypeCondition

from sc.contentrules.layout import MessageFactory as _

logger = logging.getLogger('sc.contentrules.layout')


class ViewsVocabulary(object):
    """Vocabulary factory listing available views
    """

    implements(IVocabularyFactory)

    def _get_rule(self, context):
        ''' Return rule that contains the action '''
        rule = None
        if IRule.providedBy(context):
            rule = context
        else:
            rule = aq_parent(context)
        return rule

    def _get_portal_types(self, rule):
        ''' Return a portal type condition for
            a given rule IF exists
        '''
        conditions = rule.conditions
        for condition in conditions:
            if IPortalTypeCondition.providedBy(condition):
                types = condition.check_types
                return types
        return []

    def _get_views_titles(self, views):
        result = []
        for mid in views:
            view = queryMultiAdapter((self.context, self.REQUEST),
                                     Interface, name=mid)
            if view is not None:
                menu = getUtility(IBrowserMenu, 'plone_displayviews')
                item = menu.getMenuItemByAction(self, self.REQUEST, mid)
                title = item and item.title or mid
                result.append((mid, title))
            else:
                method = getattr(self.context, mid, None)
                if method is not None:
                    # a method might be a template, script or method
                    try:
                        title = method.aq_inner.aq_explicit.title_or_id()
                    except AttributeError:
                        title = mid
                else:
                    title = mid
                result.append((mid, title))
        return result

    def _get_views(self, context):
        ''' List portal types available for this rule
        '''
        views = set()
        portal_types = getToolByName(context, 'portal_types')
        rule = self._get_rule(context)
        if rule:
            types = self._get_portal_types(rule)
            for type_name in types:
                pt = portal_types[type_name]
                pt_views = pt.getAvailableViewMethods(context)
                if not views:
                    views = set(pt_views)
                else:
                    views = views.intersection(pt_views)
        return self._get_views_titles(views)

    def __call__(self, context):
        self.context = context
        self.REQUEST = context.REQUEST
        terms = [SimpleTerm('_default_view',
                            title=_('Default Content View'))]
        views = self._get_views(context)
        for key, title in views:
            terms.append(
                SimpleTerm(
                    key,
                    title=_(title)))

        return SimpleVocabulary(terms)

ViewsVocabularyFactory = ViewsVocabulary()
