from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from collective.cart.core.tests.base import IntegrationTestCase


class TestSetup(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.types = getToolByName(self.portal, 'portal_types')
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.actions = getToolByName(self.portal, 'portal_actions')
        self.sm = getSecurityManager()

    def test_instaled__collective_cart_core(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.cart.core'))

    def test_installed__plone_app_dexterity(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('plone.app.dexterity'))

    def test_installed__collective_behavior_salable(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.salable'))

    def test_site_properties__types_not_searchable__collective_cart_core_CartContainer(self):
        properties = getToolByName(self.portal, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        self.assertIn(
            'collective.cart.core.CartContainer',
            site_properties.getProperty('types_not_searched'))

    def test_site_properties__types_not_searchable__collective_cart_core_Cart(self):
        properties = getToolByName(self.portal, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        self.assertIn(
            'collective.cart.core.Cart',
            site_properties.getProperty('types_not_searched'))

    def test_propertiestool__site_properties__types_not_searchable__collective_cart_core_CartArticle(self):
        properties = getToolByName(self.portal, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        self.assertIn(
            'collective.cart.core.CartArticle',
            site_properties.getProperty('types_not_searched'))

    def test_propertiestool__navtree_properties__metaTypesNotToList__collective_cart_core_CartContainer(self):
        properties = getToolByName(self.portal, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        self.assertIn(
            'collective.cart.core.CartContainer',
             navtree_properties.getProperty('metaTypesNotToList'))

    def test_propertiestool__navtree_properties__metaTypesNotToList__collective_cart_core_Cart(self):
        properties = getToolByName(self.portal, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        self.assertIn(
            'collective.cart.core.Cart',
             navtree_properties.getProperty('metaTypesNotToList'))

    def test_propertiestool__navtree_properties__metaTypesNotToList__collective_cart_core_CartArticle(self):
        properties = getToolByName(self.portal, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        self.assertIn(
            'collective.cart.core.CartArticle',
             navtree_properties.getProperty('metaTypesNotToList'))

    ## worlflows.xml
    def test_worlflow_installed(self):
        for item in ['cart_default_workflow']:
            self.failUnless(item in self.workflow.objectIds())

    def test_cart_folder_workflow_chain(self):
        self.failUnless('cart_container_default_workflow' in self.workflow.getChainForPortalType('collective.cart.core.CartContainer'))

    def test_cart_workflow_chain(self):
        self.failUnless('cart_default_workflow' in self.workflow.getChainForPortalType('collective.cart.core.Cart'))

    ## cart_container_default_workflow definition.xml
    def test_cart_container_default_workflow_definition_permissions(self):
        perms = ('Access contents information', 'List folder contents', 'Modify portal content', 'View')
        state = self.workflow.cart_container_default_workflow.states.addable
        for perm in perms:
            self.failUnless(perm in self.workflow.cart_container_default_workflow.permissions)
            self.assertEqual(0, state.getPermissionInfo(perm)['acquired'])
        secured_permission_roles = {
            'Modify portal content': (
                'Contributor',
                'Manager',
                'Site Administrator'
            ),
            'Access contents information': (
                'Authenticated',
            ),
            'List folder contents': (
                'Contributor',
                'Manager',
                'Site Administrator'
            ),
            'View': (
                'Authenticated',
            ),
        }
        self.assertEqual(secured_permission_roles, state.permission_roles)

    def test_cart_container_default_workflow_definition_states(self):
        self.assertEqual(['addable'], self.workflow.cart_container_default_workflow.states.objectIds())

    ## cart_default_workflow definition.xml
    def test_cart_default_workflow_definition_permissions(self):
        perms = ('Access contents information', 'List folder contents', 'Modify portal content', 'View')
        for perm in perms:
            self.failUnless(perm in self.workflow.cart_default_workflow.permissions)

    def test_cart_default_workflow_definition_states(self):
        states = ['canceled', 'shipped', 'charged', 'paid', 'created']
        for state in states:
            self.failUnless(state in self.workflow.cart_default_workflow.states.objectIds())
        items = dict(self.workflow.cart_default_workflow.states.objectItems())
        created = items.get('created')
        charged = items.get('charged')
        paid = items.get('paid')
        shipped = items.get('shipped')
        canceled = items.get('canceled')
        for item in ['charge', 'cancel']:
            self.failUnless(item in created.getTransitions())
        for item in ['pay', 'cancel', 'create']:
            self.failUnless(item in charged.getTransitions())
        for item in ['ship', 'cancel']:
            self.failUnless(item in paid.getTransitions())
        self.assertEqual((), shipped.getTransitions())
        self.assertEqual((), canceled.getTransitions())
        objs = items.values()
        perms = ('Access contents information', 'List folder contents', 'Modify portal content', 'View')
        for obj in objs:
            for perm in perms:
                self.assertEqual(0, obj.getPermissionInfo(perm)['acquired'])
        created_permission_roles = {
            'Modify portal content': (
                'Authenticated',
            ),
           'List folder contents': (
                'Authenticated',
            ),
            'Access contents information': (
                'Authenticated',
            ),
            'View': (
                'Authenticated',
            ),
        }
        self.assertEqual(created_permission_roles, created.permission_roles)
        other_permission_roles = {
            'Modify portal content': (
                'Contributor',
                'Manager',
                'Site Administrator'
            ),
           'List folder contents': (
                'Contributor',
                'Manager',
                'Site Administrator'
            ),
            'Access contents information': (
                'Authenticated',
            ),
            'View': (
                'Authenticated',
            ),
        }
        states.remove('created')
        objs = [items[state] for state in states]
        for obj in objs:
            self.assertEqual(other_permission_roles, obj.permission_roles)

    def test_cart_default_workflow_definition_transitions(self):
        transitions = ['cancel', 'pay', 'charge', 'create', 'ship']
        for transition in transitions:
            self.failUnless(transition in self.workflow.cart_default_workflow.transitions.objectIds())
        items = dict(self.workflow.cart_default_workflow.transitions.objectItems())
        charge = items.get('charge')
        pay = items.get('pay')
        ship = items.get('ship')
        cancel = items.get('cancel')
        create = items.get('create')
        self.assertEqual('charged', charge.new_state_id)
        self.assertEqual('paid', pay.new_state_id)
        self.assertEqual('shipped', ship.new_state_id)
        self.assertEqual('canceled', cancel.new_state_id)
        self.assertEqual('created', create.new_state_id)

    def test_actions__object_buttons__make_shopping_site__i18n_domain(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').make_shopping_site
        self.assertEqual(action.i18n_domain, 'collective.cart.core')

    def test_actions__object_buttons__make_shopping_site__meta_type(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').make_shopping_site
        self.assertEqual(action.meta_type, 'CMF Action')

    def test_actions__object_buttons__make_shopping_site__title(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').make_shopping_site
        self.assertEqual(action.title, 'Make Shopping Site')

    def test_actions__object_buttons__make_shopping_site__description(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').make_shopping_site
        self.assertEqual(action.description, 'Make this container shopping site.')

    def test_actions__object_buttons__make_shopping_site__url_expr(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').make_shopping_site
        self.assertEqual(
            action.url_expr, 'string:${globals_view/getCurrentObjectUrl}/@@make-shopping-site')

    def test_actions__object_buttons__make_shopping_site__available_expr(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').make_shopping_site
        self.assertEqual(
            action.available_expr, 'python: object.restrictedTraverse("not-shopping-site")()')

    def test_actions__object_buttons__make_shopping_site__permissions(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').make_shopping_site
        self.assertEqual(action.permissions, ('Manage portal',))

    def test_actions__object_buttons__make_shopping_site__visible(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').make_shopping_site
        self.assertTrue(action.visible)

    def test_actions__object_buttons__unmake_shopping_site__i18n_domain(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').unmake_shopping_site
        self.assertEqual(action.i18n_domain, 'collective.cart.core')

    def test_actions__object_buttons__unmake_shopping_site__meta_type(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').unmake_shopping_site
        self.assertEqual(action.meta_type, 'CMF Action')

    def test_actions__object_buttons__unmake_shopping_site__title(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').unmake_shopping_site
        self.assertEqual(action.title, 'Unmake Shopping Site')

    def test_actions__object_buttons__unmake_shopping_site__description(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').unmake_shopping_site
        self.assertEqual(action.description, 'Unmake this container shopping site.')

    def test_actions__object_buttons__unmake_shopping_site__url_expr(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').unmake_shopping_site
        self.assertEqual(
            action.url_expr, 'string:${globals_view/getCurrentObjectUrl}/@@unmake-shopping-site')

    def test_actions__object_buttons__unmake_shopping_site__available_expr(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').unmake_shopping_site
        self.assertEqual(
            action.available_expr, 'python: object.restrictedTraverse("is-shopping-site")()')

    def test_actions__object_buttons__unmake_shopping_site__permissions(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').unmake_shopping_site
        self.assertEqual(action.permissions, ('Manage portal',))

    def test_actions__object_buttons__unmake_shopping_site__visible(self):
        actions = getToolByName(self.portal, 'portal_actions')
        action = getattr(actions, 'object_buttons').unmake_shopping_site
        self.assertTrue(action.visible)

    def test_browserlayer(self):
        from collective.cart.core.browser.interfaces import ICollectiveCartCoreLayer
        from plone.browserlayer import utils
        self.failUnless(ICollectiveCartCoreLayer in utils.registered_layers())

    def test_rolemap__collective_cart_core_AddArticle__rolesOfPermission(self):
        permission = "collective.cart.core: Add Article"
        roles = [item['name'] for item in self.portal.rolesOfPermission(
            permission) if item['selected'] == 'SELECTED']
        roles.sort()
        self.assertEqual(roles, [
            'Contributor',
            'Manager',
            'Site Administrator',
            ])

    def test_rolemap__collective_cart_core_AddArticle__acquiredRolesAreUsedBy(self):
        permission = "collective.cart.core: Add Article"
        self.assertEqual(
            self.portal.acquiredRolesAreUsedBy(permission), 'CHECKED')

    def test_rolemap__collective_cart_core_AddCart__rolesOfPermission(self):
        permission = "collective.cart.core: Add Cart"
        roles = [item['name'] for item in self.portal.rolesOfPermission(
            permission) if item['selected'] == 'SELECTED']
        roles.sort()
        self.assertEqual(roles, [
            'Authenticated',
            ])

    def test_rolemap__collective_cart_core_AddCart__acquiredRolesAreUsedBy(self):
        permission = "collective.cart.core: Add Cart"
        self.assertEqual(
            self.portal.acquiredRolesAreUsedBy(permission), '')

    def test_rolemap__collective_cart_core_ViewCartContent__rolesOfPermission(self):
        permission = "collective.cart.core: View Cart Content"
        roles = [item['name'] for item in self.portal.rolesOfPermission(
            permission) if item['selected'] == 'SELECTED']
        roles.sort()
        self.assertEqual(roles, [
            'Contributor',
            'Manager',
            'Site Administrator',
            ])

    def test_rolemap__collective_cart_core_ViewCartContent__acquiredRolesAreUsedBy(self):
        permission = "collective.cart.core: View Cart Content"
        self.assertEqual(
            self.portal.acquiredRolesAreUsedBy(permission), 'CHECKED')

    def test_rolemap__collective_cart_core_AddCartPortlet__rolesOfPermission(self):
        permission = "collective.cart.core: Add Cart Portlet"
        roles = [item['name'] for item in self.portal.rolesOfPermission(
            permission) if item['selected'] == 'SELECTED']
        roles.sort()
        self.assertEqual(roles, [
            'Manager',
            'Site Administrator',
            ])

    def test_rolemap__collective_cart_core_AddCartPortlet__acquiredRolesAreUsedBy(self):
        permission = "collective.cart.core: Add Cart Portlet"
        self.assertEqual(
            self.portal.acquiredRolesAreUsedBy(permission), 'CHECKED')

    def test_types__collective_cart_core_Article__i18n_domain(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.i18n_domain, 'collective.cart.core')

    def test_types__collective_cart_core_Article__meta_type(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.meta_type, 'Dexterity FTI')

    def test_types__collective_cart_core_Article__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.title, 'Article')

    def test_types__collective_cart_core_Article__description(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.description, '')

    def test_types__collective_cart_core_Article__content_icon(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.getIcon(), '++resource++collective.cart.core/article.png')

    def test_types__collective_cart_core_Article__allow_discussion(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertFalse(ctype.allow_discussion)

    def test_types__collective_cart_core_Article__global_allow(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertTrue(ctype.global_allow)

    def test_types__collective_cart_core_Article__filter_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertTrue(ctype.filter_content_types)

    def test_types__collective_cart_core_Article__allowed_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.allowed_content_types, ())

    def test_types__collective_cart_core_Article__schema(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.schema, 'collective.cart.core.interfaces.IArticle')

    def test_types__collective_cart_core_Article__klass(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.klass, 'plone.dexterity.content.Container')

    def test_types__collective_cart_core_Article__add_permission(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.add_permission, 'collective.cart.core.AddArticle')

    def test_types__collective_cart_core_Article__behaviors(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(
            ctype.behaviors,
            (
                'plone.app.content.interfaces.INameFromTitle',
                'plone.app.dexterity.behaviors.metadata.IDublinCore',
                'collective.behavior.salable.interfaces.ISalable'))

    def test_types__collective_cart_core_Article__default_view(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.default_view, 'view')

    def test_types__collective_cart_core_Article__default_view_fallback(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertFalse(ctype.default_view_fallback)

    def test_types__collective_cart_core_Article__view_methods(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.view_methods, ('view',))

    def test_types__collective_cart_core_Article__default_aliases(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(
            ctype.default_aliases,
            {'edit': '@@edit', 'sharing': '@@sharing', '(Default)': '(dynamic view)', 'view': '(selected layout)'})

    def test_types__collective_cart_core_Article__action__view__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.title, 'View')

    def test_types__collective_cart_core_Article__action__view__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_core_Article__action__view__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.getActionExpression(), 'string:${folder_url}/')

    def test_types__collective_cart_core_Article__action__view__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        action = ctype.getActionObject('object/view')
        self.assertTrue(action.visible)

    def test_types__collective_cart_core_Article__action__view__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.permissions, (u'View',))

    def test_types__collective_cart_core_Article__action__edit__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.title, 'Edit')

    def test_types__collective_cart_core_Article__action__edit__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_core_Article__action__edit__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.getActionExpression(), 'string:${object_url}/edit')

    def test_types__collective_cart_core_Article__action__edit__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        action = ctype.getActionObject('object/edit')
        self.assertTrue(action.visible)

    def test_types__collective_cart_core_Article__action__edit__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.permissions, (u'Modify portal content',))

    def test_types__collective_cart_core_CartContainer__i18n_domain(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.i18n_domain, 'collective.cart.core')

    def test_types__collective_cart_core_CartContainer__meta_type(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.meta_type, 'Dexterity FTI')

    def test_types__collective_cart_core_CartContainer__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.title, 'CartContainer')

    def test_types__collective_cart_core_CartContainer__description(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.description, '')

    def test_types__collective_cart_core_CartContainer__content_icon(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.getIcon(), 'folder.gif')

    def test_types__collective_cart_core_CartContainer__allow_discussion(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertFalse(ctype.allow_discussion)

    def test_types__collective_cart_core_CartContainer__global_allow(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertFalse(ctype.global_allow)

    def test_types__collective_cart_core_CartContainer__filter_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertTrue(ctype.filter_content_types)

    def test_types__collective_cart_core_CartContainer__allowed_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.allowed_content_types, ())

    def test_types__collective_cart_core_CartContainer__schema(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.schema, 'collective.cart.core.interfaces.ICartContainer')

    def test_types__collective_cart_core_CartContainer__klass(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.klass, 'plone.dexterity.content.Container')

    def test_types__collective_cart_core_CartContainer__add_permission(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.add_permission, 'collective.cart.core.AddCartContainer')

    def test_types__collective_cart_core_CartContainer__behaviors(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.behaviors, ())

    def test_types__collective_cart_core_CartContainer__default_view(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.default_view, 'view')

    def test_types__collective_cart_core_CartContainer__default_view_fallback(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertFalse(ctype.default_view_fallback)

    def test_types__collective_cart_core_CartContainer__view_methods(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(ctype.view_methods, ('view',))

    def test_types__collective_cart_core_CartContainer__default_aliases(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        self.assertEqual(
            ctype.default_aliases,
            {'edit': '@@edit', 'sharing': '@@sharing', '(Default)': '(dynamic view)', 'view': '(selected layout)'})

    def test_types__collective_cart_core_CartContainer__action__view__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.title, 'View')

    def test_types__collective_cart_core_CartContainer__action__view__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_core_CartContainer__action__view__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.getActionExpression(), 'string:${folder_url}/')

    def test_types__collective_cart_core_CartContainer__action__view__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        action = ctype.getActionObject('object/view')
        self.assertTrue(action.visible)

    def test_types__collective_cart_core_CartContainer__action__view__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.permissions, (u'View',))

    def test_types__collective_cart_core_CartContainer__action__edit__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.title, 'Edit')

    def test_types__collective_cart_core_CartContainer__action__edit__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_core_CartContainer__action__edit__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.getActionExpression(), 'string:${object_url}/edit')

    def test_types__collective_cart_core_CartContainer__action__edit__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        action = ctype.getActionObject('object/edit')
        self.assertTrue(action.visible)

    def test_types__collective_cart_core_CartContainer__action__edit__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartContainer')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.permissions, (u'Modify portal content',))

    def test_types__collective_cart_core_Cart__i18n_domain(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.i18n_domain, 'collective.cart.core')

    def test_types__collective_cart_core_Cart__meta_type(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.meta_type, 'Dexterity FTI')

    def test_types__collective_cart_core_Cart__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.title, 'Cart')

    def test_types__collective_cart_core_Cart__description(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.description, '')

    def test_types__collective_cart_core_Cart__content_icon(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.getIcon(), '++resource++collective.cart.core/cart.png')

    def test_types__collective_cart_core_Cart__allow_discussion(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertFalse(ctype.allow_discussion)

    def test_types__collective_cart_core_Cart__global_allow(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertFalse(ctype.global_allow)

    def test_types__collective_cart_core_Cart__filter_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertTrue(ctype.filter_content_types)

    def test_types__collective_cart_core_Cart__allowed_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.allowed_content_types, ('collective.cart.core.CartArticle',))

    def test_types__collective_cart_core_Cart__schema(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.schema, 'collective.cart.core.interfaces.ICart')

    def test_types__collective_cart_core_Cart__klass(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.klass, 'plone.dexterity.content.Container')

    def test_types__collective_cart_core_Cart__add_permission(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.add_permission, 'collective.cart.core.AddCart')

    def test_types__collective_cart_core_Cart__behaviors(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.behaviors, (
            'plone.app.content.interfaces.INameFromTitle',
            'plone.app.dexterity.behaviors.metadata.IOwnership'))

    def test_types__collective_cart_core_Cart__default_view(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.default_view, 'view')

    def test_types__collective_cart_core_Cart__default_view_fallback(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertFalse(ctype.default_view_fallback)

    def test_types__collective_cart_core_Cart__view_methods(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(ctype.view_methods, ('view',))

    def test_types__collective_cart_core_Cart__default_aliases(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        self.assertEqual(
            ctype.default_aliases,
            {'edit': '@@edit', 'sharing': '@@sharing', '(Default)': '(dynamic view)', 'view': '(selected layout)'})

    def test_types__collective_cart_core_Cart__action__view__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.title, 'View')

    def test_types__collective_cart_core_Cart__action__view__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_core_Cart__action__view__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.getActionExpression(), 'string:${folder_url}/')

    def test_types__collective_cart_core_Cart__action__view__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        action = ctype.getActionObject('object/view')
        self.assertTrue(action.visible)

    def test_types__collective_cart_core_Cart__action__view__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.permissions, (u'View',))

    def test_types__collective_cart_core_Cart__action__edit__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.title, 'Edit')

    def test_types__collective_cart_core_Cart__action__edit__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_core_Cart__action__edit__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.getActionExpression(), 'string:${object_url}/edit')

    def test_types__collective_cart_core_Cart__action__edit__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        action = ctype.getActionObject('object/edit')
        self.assertTrue(action.visible)

    def test_types__collective_cart_core_Cart__action__edit__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Cart')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.permissions, (u'Modify portal content',))

    def test_types__collective_cart_core_CartArticle__i18n_domain(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.i18n_domain, 'collective.cart.core')

    def test_types__collective_cart_core_CartArticle__meta_type(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.meta_type, 'Dexterity FTI')

    def test_types__collective_cart_core_CartArticle__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.title, 'CartArticle')

    def test_types__collective_cart_core_CartArticle__description(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.description, '')

    def test_types__collective_cart_core_CartArticle__content_icon(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.getIcon(), '++resource++collective.cart.core/article.png')

    def test_types__collective_cart_core_CartArticle__allow_discussion(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertFalse(ctype.allow_discussion)

    def test_types__collective_cart_core_CartArticle__global_allow(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertFalse(ctype.global_allow)

    def test_types__collective_cart_core_CartArticle__filter_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertTrue(ctype.filter_content_types)

    def test_types__collective_cart_core_CartArticle__allowed_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.allowed_content_types, ())

    def test_types__collective_cart_core_CartArticle__schema(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.schema, 'collective.cart.core.interfaces.ICartArticle')

    def test_types__collective_cart_core_CartArticle__klass(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.klass, 'plone.dexterity.content.Container')

    def test_types__collective_cart_core_CartArticle__add_permission(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.add_permission, 'collective.cart.core.AddCartArticle')

    def test_types__collective_cart_core_CartArticle__behaviors(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.behaviors, ())

    def test_types__collective_cart_core_CartArticle__default_view(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.default_view, 'view')

    def test_types__collective_cart_core_CartArticle__default_view_fallback(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertFalse(ctype.default_view_fallback)

    def test_types__collective_cart_core_CartArticle__view_methods(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(ctype.view_methods, ('view',))

    def test_types__collective_cart_core_CartArticle__default_aliases(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        self.assertEqual(
            ctype.default_aliases,
            {'edit': '@@edit', 'sharing': '@@sharing', '(Default)': '(dynamic view)', 'view': '(selected layout)'})

    def test_types__collective_cart_core_CartArticle__action__view__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.title, 'View')

    def test_types__collective_cart_core_CartArticle__action__view__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_core_CartArticle__action__view__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.getActionExpression(), 'string:${folder_url}/')

    def test_types__collective_cart_core_CartArticle__action__view__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        action = ctype.getActionObject('object/view')
        self.assertTrue(action.visible)

    def test_types__collective_cart_core_CartArticle__action__view__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.permissions, (u'View',))

    def test_types__collective_cart_core_CartArticle__action__edit__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.title, 'Edit')

    def test_types__collective_cart_core_CartArticle__action__edit__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_core_CartArticle__action__edit__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.getActionExpression(), 'string:${object_url}/edit')

    def test_types__collective_cart_core_CartArticle__action__edit__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        action = ctype.getActionObject('object/edit')
        self.assertTrue(action.visible)

    def test_types__collective_cart_core_CartArticle__action__edit__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.CartArticle')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.permissions, (u'Modify portal content',))

    def test_uninstall__package(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        self.assertFalse(installer.isProductInstalled('collective.cart.core'))

    def test_uninstall__actions__object_buttons__make_shopping_site(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        actions = getToolByName(self.portal, 'portal_actions')
        self.assertRaises(
            AttributeError, lambda: getattr(actions, 'object_buttons').make_shopping_site)

    def test_uninstall__actions__object_buttons__unmake_shopping_site(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        actions = getToolByName(self.portal, 'portal_actions')
        self.assertRaises(
            AttributeError, lambda: getattr(actions, 'object_buttons').unmake_shopping_site)

    def test_uninstall__browserlayer(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        from collective.cart.core.browser.interfaces import ICollectiveCartCoreLayer
        from plone.browserlayer import utils
        self.failIf(ICollectiveCartCoreLayer in utils.registered_layers())

    def test_uninstall__types__collective_cart_core_Article(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        types = getToolByName(self.portal, 'portal_types')
        self.assertIsNone(types.getTypeInfo('collective.cart.core.Article'))

    def test_uninstall__types__collective_cart_core_CartContainer(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        types = getToolByName(self.portal, 'portal_types')
        self.assertIsNone(types.getTypeInfo('collective.cart.core.CartContainer'))

    def test_uninstall__types__collective_cart_core_Cart(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        types = getToolByName(self.portal, 'portal_types')
        self.assertIsNone(types.getTypeInfo('collective.cart.core.Cart'))

    def test_uninstall__types__collective_cart_core_CartArticle(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        types = getToolByName(self.portal, 'portal_types')
        self.assertIsNone(types.getTypeInfo('collective.cart.core.CartArticle'))
