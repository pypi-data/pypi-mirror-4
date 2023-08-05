# -*- coding: utf-8 -*-

try:
    # python2.6
    import json
except ImportError:
    # python2.4
    import simplejson as json

import unittest

from zope import interface
from zope.component import getMultiAdapter

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import logout

from collective.navigationtoggle.interfaces import INavigationToggleLayer
from collective.navigationtoggle.testing import NAVIGATION_TOGGLE_INTEGRATION_TESTING

class TestQueryView(unittest.TestCase):

    layer = NAVIGATION_TOGGLE_INTEGRATION_TESTING

    def _create(self, container, type_name, id, **kwargs):
        wtool = self.layer['portal'].portal_workflow
        wtool.setDefaultChain('simple_publication_workflow')
        container.invokeFactory(type_name, id, **kwargs)
        content = container[id]
        wtool.doActionFor(content, 'publish')

    def setUp(self):
        portal = self.layer['portal']
        request = self.layer['request']
        # to be removed when p.a.testing will fix https://dev.plone.org/ticket/11673
        interface.alsoProvides(request, INavigationToggleLayer)
        self._create(portal, type_name='Folder', id='section', title='Section')
        self._create(portal.section, type_name='Folder', id='subsection', title='Sub section')
        self._create(portal.section, type_name='Document', id='home', title='Section homepage')
        self._create(portal.section, type_name='Document', id='document1', title='A document')
        self._create(portal.section.subsection, type_name='Document', id='home', title='Subsection homepage')
        self.view = getMultiAdapter((portal, request), name=u"query-subelements")

    def test_default_page_not_returned(self):
        portal = self.layer['portal']
        request = self.layer['request']
        request.form['path'] = '/section'
        results = json.loads(self.view())
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], u'Sub section')
        self.assertEqual(results[1]['title'], u'Section homepage')
        self.assertEqual(results[2]['title'], u'A document')
        portal.section.setDefaultPage('home')
        results = json.loads(self.view())
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], u'Sub section')
        self.assertEqual(results[1]['title'], u'A document')

    def test_only_default_page_like_empty_folder(self):
        portal = self.layer['portal']
        request = self.layer['request']
        request.form['path'] = '/section/subsection'
        results = json.loads(self.view())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], u'Subsection homepage')
        portal.section.subsection.setDefaultPage('home')
        results = json.loads(self.view())
        self.assertEqual(len(results), 0)
        self.assertEqual(results, [])

    def test_metaTypesNotToList_usage(self):
        portal = self.layer['portal']
        request = self.layer['request']
        request.form['path'] = '/section'
        metaTypesNotToList = list(portal.portal_properties.navtree_properties.metaTypesNotToList)
        metaTypesNotToList.append('Folder')
        portal.portal_properties.navtree_properties.metaTypesNotToList = metaTypesNotToList
        results = json.loads(self.view())
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], u'Section homepage')
        self.assertEqual(results[1]['title'], u'A document')

    def test_workflow(self):
        portal = self.layer['portal']
        portal.portal_workflow.doActionFor(portal.section.document1, 'retract')
        logout()
        request = self.layer['request']
        request.form['path'] = '/section'
        results = json.loads(self.view())
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], u'Sub section')
        self.assertEqual(results[1]['title'], u'Section homepage')

