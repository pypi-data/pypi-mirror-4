from Products.CMFCore.utils import getToolByName
from collective.cart.core.tests.base import IntegrationTestCase


def get_action(obj, category, action):
    """Get action.

    :param obj: A content type.
    :type obj: object

    :param category: Action category such as object and object_buttons.
    :type category: str

    :param action: Name of action.
    :type actin: str

    :rtype: action object
    """
    return getattr(getattr(getToolByName(obj, 'portal_actions'), category), action)


class TestSetup(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_instaled__collective_cart_core(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.cart.core'))

    def test_installed__plone_app_dexterity(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('plone.app.dexterity'))

    def test_installed__collective_behavior_salable(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.salable'))

    def test_actions__object_orders__meta_type(self):
        action = get_action(self.portal, 'object', 'orders')
        self.assertEqual(action.meta_type, 'CMF Action')

    def test_actions__object_orders__title(self):
        action = get_action(self.portal, 'object', 'orders')
        self.assertEqual(action.title, 'Orders')

    def test_actions__object_orders__description(self):
        action = get_action(self.portal, 'object', 'orders')
        self.assertEqual(action.description, 'Show list of orders.')

    def test_actions__object_orders__url_expr(self):
        action = get_action(self.portal, 'object', 'orders')
        self.assertEqual(
            action.url_expr, 'string:${globals_view/getCurrentFolderUrl}/@@orders')

    def test_actions__object_orders__available_expr(self):
        action = get_action(self.portal, 'object', 'orders')
        self.assertEqual(
            action.available_expr, 'python: object.restrictedTraverse("is-shopping-site")()')

    def test_actions__object_orders__permissions(self):
        action = get_action(self.portal, 'object', 'orders')
        self.assertEqual(action.permissions, ('Modify portal content',))

    def test_actions__object_orders__visible(self):
        action = get_action(self.portal, 'object', 'orders')
        self.assertTrue(action.visible)

    def test_actions__object_buttons__make_shopping_site__meta_type(self):
        action = get_action(self.portal, 'object_buttons', 'make_shopping_site')
        self.assertEqual(action.meta_type, 'CMF Action')

    def test_actions__object_buttons__make_shopping_site__title(self):
        action = get_action(self.portal, 'object_buttons', 'make_shopping_site')
        self.assertEqual(action.title, 'Make Shopping Site')

    def test_actions__object_buttons__make_shopping_site__description(self):
        action = get_action(self.portal, 'object_buttons', 'make_shopping_site')
        self.assertEqual(action.description, 'Make this container shopping site.')

    def test_actions__object_buttons__make_shopping_site__url_expr(self):
        action = get_action(self.portal, 'object_buttons', 'make_shopping_site')
        self.assertEqual(
            action.url_expr, 'string:${globals_view/getCurrentFolderUrl}/@@make-shopping-site')

    def test_actions__object_buttons__make_shopping_site__available_expr(self):
        action = get_action(self.portal, 'object_buttons', 'make_shopping_site')
        self.assertEqual(
            action.available_expr, 'python: object.restrictedTraverse("not-shopping-site")()')

    def test_actions__object_buttons__make_shopping_site__permissions(self):
        action = get_action(self.portal, 'object_buttons', 'make_shopping_site')
        self.assertEqual(action.permissions, ('Manage portal',))

    def test_actions__object_buttons__make_shopping_site__visible(self):
        action = get_action(self.portal, 'object_buttons', 'make_shopping_site')
        self.assertTrue(action.visible)

    def test_actions__object_buttons__unmake_shopping_site__meta_type(self):
        action = get_action(self.portal, 'object_buttons', 'unmake_shopping_site')
        self.assertEqual(action.meta_type, 'CMF Action')

    def test_actions__object_buttons__unmake_shopping_site__title(self):
        action = get_action(self.portal, 'object_buttons', 'unmake_shopping_site')
        self.assertEqual(action.title, 'Unmake Shopping Site')

    def test_actions__object_buttons__unmake_shopping_site__description(self):
        action = get_action(self.portal, 'object_buttons', 'unmake_shopping_site')
        self.assertEqual(action.description, 'Unmake this container shopping site.')

    def test_actions__object_buttons__unmake_shopping_site__url_expr(self):
        action = get_action(self.portal, 'object_buttons', 'unmake_shopping_site')
        self.assertEqual(
            action.url_expr, 'string:${globals_view/getCurrentFolderUrl}/@@unmake-shopping-site')

    def test_actions__object_buttons__unmake_shopping_site__available_expr(self):
        action = get_action(self.portal, 'object_buttons', 'unmake_shopping_site')
        self.assertEqual(
            action.available_expr, 'python: object.restrictedTraverse("is-shopping-site")()')

    def test_actions__object_buttons__unmake_shopping_site__permissions(self):
        action = get_action(self.portal, 'object_buttons', 'unmake_shopping_site')
        self.assertEqual(action.permissions, ('Manage portal',))

    def test_actions__object_buttons__unmake_shopping_site__visible(self):
        action = get_action(self.portal, 'object_buttons', 'unmake_shopping_site')
        self.assertTrue(action.visible)

    def test_metadata__version(self):
        setup = getToolByName(self.portal, 'portal_setup')
        self.assertEqual(setup.getVersionForProfile('profile-collective.cart.core:default'), u'3')

    def test_site_properties__types_not_searchable__collective_cart_core_CartContainer(self):
        properties = getToolByName(self.portal, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        self.assertIn('collective.cart.core.CartContainer',
            site_properties.getProperty('types_not_searched'))

    def test_site_properties__types_not_searchable__collective_cart_core_Cart(self):
        properties = getToolByName(self.portal, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        self.assertIn('collective.cart.core.Cart',
            site_properties.getProperty('types_not_searched'))

    def test_propertiestool__site_properties__types_not_searchable__collective_cart_core_CartArticle(self):
        properties = getToolByName(self.portal, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        self.assertIn('collective.cart.core.CartArticle',
            site_properties.getProperty('types_not_searched'))

    def test_propertiestool__navtree_properties__metaTypesNotToList__collective_cart_core_CartContainer(self):
        properties = getToolByName(self.portal, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        self.assertIn('collective.cart.core.CartContainer',
             navtree_properties.getProperty('metaTypesNotToList'))

    def test_propertiestool__navtree_properties__metaTypesNotToList__collective_cart_core_Cart(self):
        properties = getToolByName(self.portal, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        self.assertIn('collective.cart.core.Cart',
             navtree_properties.getProperty('metaTypesNotToList'))

    def test_propertiestool__navtree_properties__metaTypesNotToList__collective_cart_core_CartArticle(self):
        properties = getToolByName(self.portal, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        self.assertIn('collective.cart.core.CartArticle',
             navtree_properties.getProperty('metaTypesNotToList'))

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
            'Site Administrator'])

    def test_rolemap__collective_cart_core_AddArticle__acquiredRolesAreUsedBy(self):
        permission = "collective.cart.core: Add Article"
        self.assertEqual(
            self.portal.acquiredRolesAreUsedBy(permission), 'CHECKED')

    def test_rolemap__collective_cart_core_AddCart__rolesOfPermission(self):
        permission = "collective.cart.core: Add Cart"
        roles = [item['name'] for item in self.portal.rolesOfPermission(
            permission) if item['selected'] == 'SELECTED']
        roles.sort()
        self.assertEqual(roles, ['Authenticated'])

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
            'Site Administrator'])

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
            'Site Administrator'])

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
        self.assertEqual(ctype.title, 'Cart Container')

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
        self.assertEqual(ctype.behaviors, ('plone.app.content.interfaces.INameFromTitle',))

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
        self.assertEqual(ctype.title, 'Cart Article')

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

    def test_workflow__type__collective_cart_core_Cart(self):
        workflow = getToolByName(self.portal, 'portal_workflow')
        self.assertEqual(workflow.getChainForPortalType('collective.cart.core.Cart'),
            ('cart_default_workflow', ))

    def get_workflow(self, name):
        workflow = getToolByName(self.portal, 'portal_workflow')
        return workflow[name]

    def test_cart_default_workflow__description(self):
        workflow = self.get_workflow('cart_default_workflow')
        self.assertEqual(workflow.description, '')

    def test_cart_default_workflow__initial_state(self):
        workflow = self.get_workflow('cart_default_workflow')
        self.assertEqual(workflow.initial_state, 'created')

    def test_cart_default_workflow__manager_bypass(self):
        workflow = self.get_workflow('cart_default_workflow')
        self.assertFalse(workflow.manager_bypass)

    def test_cart_default_workflow__state_variable(self):
        workflow = self.get_workflow('cart_default_workflow')
        self.assertEqual(workflow.state_var, 'review_state')

    def test_cart_default_workflow__title(self):
        workflow = self.get_workflow('cart_default_workflow')
        self.assertEqual(workflow.title, 'Cart Default Workflow')

    def test_cart_default_workflow__permissions(self):
        workflow = self.get_workflow('cart_default_workflow')
        self.assertEqual(workflow.permissions, (
            'Access contents information',
            'List folder contents',
            'Modify portal content',
            'View'))

    def test_cart_default_workflow__states__created__title(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.created
        self.assertEqual(state.title, 'Created')

    def test_cart_default_workflow__states__created__description(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.created
        self.assertEqual(state.description, '')

    def test_cart_default_workflow__states__created__permission__Access_contents_information(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.created
        self.assertEqual(state.getPermissionInfo('Access contents information'), {
            'acquired': 0,
            'roles': ['Authenticated'],
        })

    def test_cart_default_workflow__states__created__permission__List_folder_contents(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.created
        self.assertEqual(state.getPermissionInfo('List folder contents'), {
            'acquired': 0,
            'roles': ['Authenticated'],
        })

    def test_cart_default_workflow__states__created__permission__Modify_portal_content(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.created
        self.assertEqual(state.getPermissionInfo('Modify portal content'), {
            'acquired': 0,
            'roles': ['Authenticated'],
        })

    def test_cart_default_workflow__states__created__permission__View(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.created
        self.assertEqual(state.getPermissionInfo('View'), {
            'acquired': 0,
            'roles': ['Authenticated'],
        })

    def test_cart_default_workflow__states__ordered__title(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.ordered
        self.assertEqual(state.title, 'Ordered')

    def test_cart_default_workflow__states__ordered__description(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.ordered
        self.assertEqual(state.description, '')

    def test_cart_default_workflow__states__ordered__permission__Access_contents_information(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.ordered
        self.assertEqual(state.getPermissionInfo('Access contents information'), {
            'acquired': 0,
            'roles': ['Authenticated'],
        })

    def test_cart_default_workflow__states__ordered__permission__List_folder_contents(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.ordered
        self.assertEqual(state.getPermissionInfo('List folder contents'), {
            'acquired': 0,
            'roles': ['Contributor', 'Manager', 'Site Administrator'],
        })

    def test_cart_default_workflow__states__ordered__permission__Modify_portal_content(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.ordered
        self.assertEqual(state.getPermissionInfo('Modify portal content'), {
            'acquired': 0,
            'roles': ['Contributor', 'Manager', 'Site Administrator'],
        })

    def test_cart_default_workflow__states__ordered__permission__View(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.ordered
        self.assertEqual(state.getPermissionInfo('View'), {
            'acquired': 0,
            'roles': ['Authenticated'],
        })

    def test_cart_default_workflow__states__paid__title(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.paid
        self.assertEqual(state.title, 'Paid')

    def test_cart_default_workflow__states__paid__description(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.paid
        self.assertEqual(state.description, '')

    def test_cart_default_workflow__states__paid__permission__Access_contents_information(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.paid
        self.assertEqual(state.getPermissionInfo('Access contents information'), {
            'acquired': 0,
            'roles': ['Authenticated'],
        })

    def test_cart_default_workflow__states__paid__permission__List_folder_contents(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.paid
        self.assertEqual(state.getPermissionInfo('List folder contents'), {
            'acquired': 0,
            'roles': ['Contributor', 'Manager', 'Site Administrator'],
        })

    def test_cart_default_workflow__states__paid__permission__Modify_portal_content(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.paid
        self.assertEqual(state.getPermissionInfo('Modify portal content'), {
            'acquired': 0,
            'roles': ['Contributor', 'Manager', 'Site Administrator'],
        })

    def test_cart_default_workflow__states__paid__permission__View(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.paid
        self.assertEqual(state.getPermissionInfo('View'), {
            'acquired': 0,
            'roles': ['Authenticated'],
        })

    def test_cart_default_workflow__states__shipped__title(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.shipped
        self.assertEqual(state.title, 'Shipped')

    def test_cart_default_workflow__states__shipped__description(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.shipped
        self.assertEqual(state.description, '')

    def test_cart_default_workflow__states__shipped__permission__Access_contents_information(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.shipped
        self.assertEqual(state.getPermissionInfo('Access contents information'), {
            'acquired': 0,
            'roles': ['Authenticated'],
        })

    def test_cart_default_workflow__states__shipped__permission__List_folder_contents(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.shipped
        self.assertEqual(state.getPermissionInfo('List folder contents'), {
            'acquired': 0,
            'roles': ['Contributor', 'Manager', 'Site Administrator'],
        })

    def test_cart_default_workflow__states__shipped__permission__Modify_portal_content(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.shipped
        self.assertEqual(state.getPermissionInfo('Modify portal content'), {
            'acquired': 0,
            'roles': ['Contributor', 'Manager', 'Site Administrator'],
        })

    def test_cart_default_workflow__states__shipped__permission__View(self):
        workflow = self.get_workflow('cart_default_workflow')
        state = workflow.states.shipped
        self.assertEqual(state.getPermissionInfo('View'), {
            'acquired': 0,
            'roles': ['Authenticated'],
        })

    def test_cart_default_workflow__transitions__created__after_script(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.created
        self.assertEqual(transition.after_script_name, '')

    def test_cart_default_workflow__transitions__created__before_script(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.created
        self.assertEqual(transition.script_name, '')

    def test_cart_default_workflow__transitions__created__new_state(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.created
        self.assertEqual(transition.new_state_id, 'created')

    def test_cart_default_workflow__transitions__created__title(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.created
        self.assertEqual(transition.title, 'State to created')

    def test_cart_default_workflow__transitions__created__trigger(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.created
        self.assertEqual(transition.trigger_type, 1)

    def test_cart_default_workflow__transitions__created__action__category(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.created
        self.assertEqual(transition.actbox_category, 'workflow')

    def test_cart_default_workflow__transitions__created__action__icon(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.created
        self.assertEqual(transition.actbox_icon, '')

    def test_cart_default_workflow__transitions__created__action__url(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.created
        self.assertEqual(transition.actbox_url,
            '%(content_url)s/content_status_modify?workflow_action=created')

    def test_cart_default_workflow__transitions__created__guard(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.created
        self.assertIsNone(transition.guard)

    def test_cart_default_workflow__transitions__ordered__after_script(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.ordered
        self.assertEqual(transition.after_script_name, '')

    def test_cart_default_workflow__transitions__ordered__before_script(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.ordered
        self.assertEqual(transition.script_name, '')

    def test_cart_default_workflow__transitions__ordered__new_state(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.ordered
        self.assertEqual(transition.new_state_id, 'ordered')

    def test_cart_default_workflow__transitions__ordered__title(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.ordered
        self.assertEqual(transition.title, 'State to ordered')

    def test_cart_default_workflow__transitions__ordered__trigger(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.ordered
        self.assertEqual(transition.trigger_type, 1)

    def test_cart_default_workflow__transitions__ordered__action__category(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.ordered
        self.assertEqual(transition.actbox_category, 'workflow')

    def test_cart_default_workflow__transitions__ordered__action__icon(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.ordered
        self.assertEqual(transition.actbox_icon, '')

    def test_cart_default_workflow__transitions__ordered__action__url(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.ordered
        self.assertEqual(transition.actbox_url,
            '%(content_url)s/content_status_modify?workflow_action=ordered')

    def test_cart_default_workflow__transitions__ordered__guard(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.ordered
        self.assertIsNone(transition.guard)

    def test_cart_default_workflow__transitions__paid__after_script(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.paid
        self.assertEqual(transition.after_script_name, '')

    def test_cart_default_workflow__transitions__paid__before_script(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.paid
        self.assertEqual(transition.script_name, '')

    def test_cart_default_workflow__transitions__paid__new_state(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.paid
        self.assertEqual(transition.new_state_id, 'paid')

    def test_cart_default_workflow__transitions__paid__title(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.paid
        self.assertEqual(transition.title, 'State to Paid')

    def test_cart_default_workflow__transitions__paid__trigger(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.paid
        self.assertEqual(transition.trigger_type, 1)

    def test_cart_default_workflow__transitions__paid__action__category(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.paid
        self.assertEqual(transition.actbox_category, 'workflow')

    def test_cart_default_workflow__transitions__paid__action__icon(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.paid
        self.assertEqual(transition.actbox_icon, '')

    def test_cart_default_workflow__transitions__paid__action__url(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.paid
        self.assertEqual(transition.actbox_url,
            '%(content_url)s/content_status_modify?workflow_action=paid')

    def test_cart_default_workflow__transitions__paid__guard(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.paid
        self.assertIsNone(transition.guard)

    def test_cart_default_workflow__transitions__shipped__after_script(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.shipped
        self.assertEqual(transition.after_script_name, '')

    def test_cart_default_workflow__transitions__shipped__before_script(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.shipped
        self.assertEqual(transition.script_name, '')

    def test_cart_default_workflow__transitions__shipped__new_state(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.shipped
        self.assertEqual(transition.new_state_id, 'shipped')

    def test_cart_default_workflow__transitions__shipped__title(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.shipped
        self.assertEqual(transition.title, 'State to Shipped')

    def test_cart_default_workflow__transitions__shipped__trigger(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.shipped
        self.assertEqual(transition.trigger_type, 1)

    def test_cart_default_workflow__transitions__shipped__action__category(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.shipped
        self.assertEqual(transition.actbox_category, 'workflow')

    def test_cart_default_workflow__transitions__shipped__action__icon(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.shipped
        self.assertEqual(transition.actbox_icon, '')

    def test_cart_default_workflow__transitions__shipped__action__url(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.shipped
        self.assertEqual(transition.actbox_url,
            '%(content_url)s/content_status_modify?workflow_action=shipped')

    def test_cart_default_workflow__transitions__shipped__guard(self):
        workflow = self.get_workflow('cart_default_workflow')
        transition = workflow.transitions.shipped
        self.assertIsNone(transition.guard)

    def test_cart_default_workflow__variables__action__for_catalog(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.action
        self.assertFalse(variable.for_catalog)

    def test_cart_default_workflow__variables__action__for_status(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.action
        self.assertTrue(variable.for_status)

    def test_cart_default_workflow__variables__action__updata_always(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.action
        self.assertTrue(variable.update_always)

    def test_cart_default_workflow__variables__action__description(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.action
        self.assertEqual(variable.description, 'Previous transition')

    def test_cart_default_workflow__variables__action__default(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.action
        self.assertEqual(variable.getDefaultExprText(), 'transition/getId|nothing')

    def test_cart_default_workflow__variables__action__guard(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.action
        self.assertIsNone(variable.info_guard)

    def test_cart_default_workflow__variables__actor__for_catalog(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.actor
        self.assertFalse(variable.for_catalog)

    def test_cart_default_workflow__variables__actor__for_status(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.actor
        self.assertTrue(variable.for_status)

    def test_cart_default_workflow__variables__actor__updata_always(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.actor
        self.assertTrue(variable.update_always)

    def test_cart_default_workflow__variables__actor__description(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.actor
        self.assertEqual(variable.description, 'The ID of the user who performed the last transition')

    def test_cart_default_workflow__variables__actor__default(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.actor
        self.assertEqual(variable.getDefaultExprText(), 'user/getId')

    def test_cart_default_workflow__variables__actor__guard(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.actor
        self.assertIsNone(variable.info_guard)

    def test_cart_default_workflow__variables__comments__for_catalog(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.comments
        self.assertFalse(variable.for_catalog)

    def test_cart_default_workflow__variables__comments__for_status(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.comments
        self.assertTrue(variable.for_status)

    def test_cart_default_workflow__variables__comments__updata_always(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.comments
        self.assertTrue(variable.update_always)

    def test_cart_default_workflow__variables__comments__description(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.comments
        self.assertEqual(variable.description, 'Comment about the last transition')

    def test_cart_default_workflow__variables__comments__default(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.comments
        self.assertEqual(variable.getDefaultExprText(),
            "python:state_change.kwargs.get('comment', '')")

    def test_cart_default_workflow__variables__comments__guard(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.comments
        self.assertIsNone(variable.info_guard)

    def test_cart_default_workflow__variables__review_history__for_catalog(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.review_history
        self.assertFalse(variable.for_catalog)

    def test_cart_default_workflow__variables__review_history__for_status(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.review_history
        self.assertFalse(variable.for_status)

    def test_cart_default_workflow__variables__review_history__updata_always(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.review_history
        self.assertFalse(variable.update_always)

    def test_cart_default_workflow__variables__review_history__description(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.review_history
        self.assertEqual(variable.description, 'Provides access to workflow history')

    def test_cart_default_workflow__variables__review_history__default(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.review_history
        self.assertEqual(variable.getDefaultExprText(),
            "state_change/getHistory")

    def test_cart_default_workflow__variables__review_history__guard(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.review_history
        self.assertEqual(variable.info_guard.permissions,
            ('Request review', 'Review portal content'))

    def test_cart_default_workflow__variables__time__for_catalog(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.time
        self.assertFalse(variable.for_catalog)

    def test_cart_default_workflow__variables__time__for_status(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.time
        self.assertTrue(variable.for_status)

    def test_cart_default_workflow__variables__time__updata_always(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.time
        self.assertTrue(variable.update_always)

    def test_cart_default_workflow__variables__time__description(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.time
        self.assertEqual(variable.description, 'When the previous transition was performed')

    def test_cart_default_workflow__variables__time__default(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.time
        self.assertEqual(variable.getDefaultExprText(),
            "state_change/getDateTime")

    def test_cart_default_workflow__variables__time__guard(self):
        workflow = self.get_workflow('cart_default_workflow')
        variable = workflow.variables.time
        self.assertIsNone(variable.info_guard)

    def test_uninstall__package(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        self.assertFalse(installer.isProductInstalled('collective.cart.core'))

    def test_uninstall__actions__object_buttons__make_shopping_site(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        self.assertRaises(
            AttributeError, lambda: get_action(self.portal, 'object_buttons', 'make_shopping_site'))

    def test_uninstall__actions__object_buttons__unmake_shopping_site(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.core'])
        self.assertRaises(
            AttributeError, lambda: get_action(self.portal, 'object_buttons', 'unmake_shopping_site'))

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
