from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.actions.move import MoveAction
from plone.app.contentrules.rule import Rule

from collective.contentrules.linguatarget.actions import LinguaMoveAction
from collective.contentrules.linguatarget.actions import LinguaMoveEditForm
import collective.contentrules.linguatarget

from Products.PloneTestCase.setup import default_user

ptc.setupPloneSite()

class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, obj):
        self.object = obj

# Since we do not need to quick-install anything or register a Zope 2 style
# product, we can use a simple layer that's set up after the Plone site has 
# been created above
class TestLinguaMoveAction(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.contentrules.linguatarget)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'target')
        self.portal.target.addTranslation('de')
        self.login(default_user)
        self.folder.invokeFactory('Document', 'd1')
        self.folder.d1.addTranslation('de')

    def testRegistered(self): 
        element = getUtility(IRuleAction, name="collective.contentrules.linguatarget.LinguaMoveAction")
        self.assertEquals('addLinguaMoveAction', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testInvokeAddView(self): 
        element = getUtility(IRuleAction, name="collective.contentrules.linguatarget.LinguaMoveAction")
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)

        addview.createAndAdd(data={
                'copy_to_translated_parent': True,
                'target_folder': '/target' })

        e = rule.actions[0]
        self.failUnless(isinstance(e, LinguaMoveAction))
        self.assertEquals('/target', e.target_folder)
        self.assertEquals(True, e.move_to_translated_parent)

    def testInvokeEditView(self): 
        element = getUtility(IRuleAction, name="collective.contentrules.linguatarget.LinguaMoveAction")
        e = LinguaMoveAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, LinguaMoveEditForm))

    def testExecute(self): 
        e = LinguaMoveAction()
        e.target_folder = '/target'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1' in self.folder.objectIds())
        self.failUnless('d1' in self.portal.target.objectIds())

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.get('d1-de'))), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1-de' in self.folder.objectIds())
        self.failUnless('d1-de' in self.portal.get('target-de').objectIds())

    def testExecuteWithError(self): 
        e = LinguaMoveAction()
        e.target_folder = '/dummy'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(False, ex())
        
        self.failUnless('d1' in self.folder.objectIds())
        self.failIf('d1' in self.portal.target.objectIds())

    def testExecuteWithNamingConflict(self):
        self.setRoles(('Manager',))
        self.portal.target.invokeFactory('Document', 'd1')
        self.setRoles(('Member',))
        
        e = LinguaMoveAction()
        e.target_folder = '/target'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1' in self.folder.objectIds())
        self.failUnless('d1' in self.portal.target.objectIds())
        self.failUnless('d1.1' in self.portal.target.objectIds())
        
    def testExecuteWithSameSourceAndTargetFolder(self):
        self.setRoles(('Manager',))
        self.portal.target.invokeFactory('Document', 'd1')
        self.setRoles(('Member',))
        
        e = LinguaMoveAction()
        e.target_folder = '/target'
        
        ex = getMultiAdapter((self.portal.target, e, DummyEvent(self.portal.target.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.assertEquals(['d1'], list(self.portal.target.objectIds()))

    def testNonLinguaExecute(self): 
        e = MoveAction()
        e.target_folder = '/target'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1' in self.folder.objectIds())
        self.failUnless('d1' in self.portal.target.objectIds())

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.get('d1-de'))), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1-de' in self.folder.objectIds())
        self.failUnless('d1-de' in self.portal.get('target').objectIds())

    def testObjectWithNoLanguage(self): 
        e = LinguaMoveAction()
        e.target_folder = '/target'
        
        self.folder.d1.setLanguage('')
        self.assertEquals(self.folder.d1.getLanguage(), '')

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1' in self.folder.objectIds())
        self.failUnless('d1' in self.portal.target.objectIds())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLinguaMoveAction))
    return suite

