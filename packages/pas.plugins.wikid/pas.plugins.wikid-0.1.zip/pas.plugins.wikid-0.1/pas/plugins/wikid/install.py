from AccessControl.Permissions import manage_users
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService import registerMultiPlugin

import plugin


manage_addWiKIDAuthPluginForm = PageTemplateFile('www/wikidAdd', globals(), __name__='manage_addWiKIDAuthPluginForm')


def manage_addWiKIDAuthPlugin(dispatcher, id, title=None, REQUEST=None):
    """ Add a WiKIDAuthPlugin to a Pluggable Auth Service. """

    obj = plugin.WiKIDAuthPlugin(id, title)
    dispatcher._setObject(obj.getId(), obj)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_workspace'
                                     '?manage_tabs_message='
                                     'WiKIDAuthPlugin+added.'
                                     % dispatcher.absolute_url())


def register_wikid_plugin():
    try:
        registerMultiPlugin(plugin.WiKIDAuthPlugin.meta_type)
    except RuntimeError:
        # make refresh users happy
        pass


def register_wikid_plugin_class(context):
    context.registerClass(plugin.WiKIDAuthPlugin,
                          permission=manage_users,
                          constructors=(manage_addWiKIDAuthPluginForm,
                                        manage_addWiKIDAuthPlugin),
                          visibility = None,
                          icon='www/WiKID.png')
