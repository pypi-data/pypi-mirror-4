# -*- coding:utf-8 -*-

import unittest2 as unittest

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from zope.interface import implements
from zope.component import getUtility
from zope.component import getMultiAdapter

from zope.component.interfaces import IObjectEvent

from zope.schema.interfaces import IVocabularyFactory

from plone.app.contentrules.rule import Rule

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.contentrules.rule.interfaces import IExecutable

from sc.contentrules.layout.config import VOCAB

from sc.contentrules.layout.actions.layout import SetLayoutAction
from sc.contentrules.layout.actions.layout import SetLayoutEditForm

from sc.contentrules.layout.testing import INTEGRATION_TESTING


class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object


class TestSetLayoutAction(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'folder')
        self.folder = self.portal['folder']
        sub_folder_id = self.folder.invokeFactory('Folder', 'sub_folder')
        self.sub_folder = self.folder[sub_folder_id]

    def testRegistered(self):
        element = getUtility(IRuleAction,
                             name='sc.contentrules.actions.layout')
        self.assertEquals('sc.contentrules.actions.layout',
                          element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction,
                             name='sc.contentrules.actions.layout')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST),
                                 name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)

        addview.createAndAdd(data={'layout': 'folder_summary_view'})

        e = rule.actions[0]
        self.failUnless(isinstance(e, SetLayoutAction))
        self.assertEquals('folder_summary_view', e.layout)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction,
                             name='sc.contentrules.actions.layout')
        e = SetLayoutAction()
        editview = getMultiAdapter((e, self.folder.REQUEST),
                                   name=element.editview)
        self.failUnless(isinstance(editview, SetLayoutEditForm))

    def testExecute(self):
        e = SetLayoutAction()
        e.layout = 'folder_summary_view'

        ex = getMultiAdapter((self.folder, e,
                             DummyEvent(self.sub_folder)),
                             IExecutable)
        self.assertEquals(True, ex())

        self.assertEquals(self.sub_folder.layout, e.layout)

    def testExecuteWithError(self):
        e = SetLayoutAction()
        e.layout = 'document_view'

        ex = getMultiAdapter((self.folder, e,
                             DummyEvent(self.sub_folder)),
                             IExecutable)
        self.assertEquals(False, ex())
        # Layout not set
        self.assertEquals(hasattr(self.sub_folder, 'layout'), False)


class TestViewsVocab(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'folder')
        self.folder = self.portal['folder']
        sub_folder_id = self.folder.invokeFactory('Folder', 'sub_folder')
        self.sub_folder = self.folder[sub_folder_id]
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        self.rule = self.portal.restrictedTraverse('++rule++foo')

    def _add_condition(self, rule, types=['Folder', ]):
        element = getUtility(IRuleCondition,
                             name='plone.conditions.PortalType')
        adding = getMultiAdapter((rule, self.portal.REQUEST),
                                 name='+condition')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)

        addview.createAndAdd(data={'check_types': types})

    def _add_action(self, rule, view='_default_view'):
        element = getUtility(IRuleAction,
                             name='sc.contentrules.actions.layout')
        adding = getMultiAdapter((rule, self.portal.REQUEST),
                                 name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)

        addview.createAndAdd(data={'layout': view})

    def testRuleWithoutCondition(self):
        rule = self.rule
        self._add_action(rule)
        util = getUtility(IVocabularyFactory, VOCAB)
        vocab = util(rule)
        self.assertEquals(len(vocab.by_token), 1)

    def testRuleWithCondition(self):
        rule = self.rule
        self._add_condition(rule)
        self._add_action(rule)
        util = getUtility(IVocabularyFactory, VOCAB)
        vocab = util(rule)
        self.assertEquals(len(vocab.by_token), 6)

    def testRuleWithPTCollection(self):
        rule = self.rule
        self._add_condition(rule, types=['Collection', ])
        self._add_action(rule)
        util = getUtility(IVocabularyFactory, VOCAB)
        vocab = util(rule)
        self.assertEquals(len(vocab.by_token), 6)

    def testRuleWithConditionAndTwoTypes(self):
        rule = self.rule
        # Folder and Document have no intersection between their
        # available views, so our rule should return just _default_view
        self._add_condition(rule, ['Folder', 'Document'])
        self._add_action(rule)
        util = getUtility(IVocabularyFactory, VOCAB)
        vocab = util(rule)
        self.assertEquals(len(vocab.by_token), 1)


class TestActionAndCondition(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'folder')
        self.folder = self.portal['folder']
        sub_folder_id = self.folder.invokeFactory('Folder', 'sub_folder')
        self.sub_folder = self.folder[sub_folder_id]
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        self.rule = self.portal.restrictedTraverse('++rule++foo')

    def _add_condition(self, rule, types=['Folder', ]):
        element = getUtility(IRuleCondition,
                             name='plone.conditions.PortalType')
        adding = getMultiAdapter((rule, self.portal.REQUEST),
                                 name='+condition')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)

        addview.createAndAdd(data={'check_types': types})

    def _add_action(self, rule, view='_default_view'):
        element = getUtility(IRuleAction,
                             name='sc.contentrules.actions.layout')
        adding = getMultiAdapter((rule, self.portal.REQUEST),
                                 name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)

        addview.createAndAdd(data={'layout': view})

    def testActionWithoutPTCondition(self):
        rule = self.rule
        self._add_action(rule)
        e = rule.actions[0]
        ex = getMultiAdapter((self.folder, e,
                             DummyEvent(self.sub_folder)),
                             IExecutable)
        self.assertEquals(True, ex())
        # Layout should not be set (_default_view does nothing)
        self.failIf(hasattr(self.sub_folder, 'layout'))

    def testActionWithPTCondition(self):
        rule = self.rule
        self._add_condition(rule)
        self._add_action(rule, 'folder_summary_view')
        condition = rule.conditions[0]
        action = rule.actions[0]

        # Condition should be met
        ex = getMultiAdapter((self.folder, condition,
                             DummyEvent(self.sub_folder)),
                             IExecutable)
        self.assertEquals(True, ex())

        # Action will be executed
        ex = getMultiAdapter((self.folder, action,
                             DummyEvent(self.sub_folder)),
                             IExecutable)
        self.assertEquals(True, ex())

        self.assertEquals(self.sub_folder.layout, 'folder_summary_view')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
