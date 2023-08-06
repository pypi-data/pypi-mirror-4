"""WiKIDAuthPlugin
Copyright(C), 2008, WiKID Systems, Inc - ALL RIGHTS RESERVED

This software is licensed under the Terms and Conditions contained within the
LICENSE.txt file that accompanied this software.  Any inquiries concerning the
scope or enforceability of the license should be addressed to:

WiKID Systems, Inc.
1350 Spring St.
Suite 300
Atlanta, Ga 30309
info at wikidsystems.com
866-244-1876
"""

import os
from AccessControl import ClassSecurityInfo
from AccessControl.requestmethod import postonly

from Globals import InitializeClass
from OFS.Cache import Cacheable

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.CMFCore.permissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from  pywClient import pywClient


class WiKIDAuthPlugin(BasePlugin, Cacheable):

    """ PAS plugin for using WiKID credentials to log in.
    """

    meta_type = 'WiKIDAuthPlugin'

    security = ClassSecurityInfo()

    # ZMI tab for configuration page
    manage_options = (({'label': 'Configuration',
                        'action': 'manage_config'},)
                      + BasePlugin.manage_options
                      + Cacheable.manage_options)

    security.declareProtected(ManagePortal, 'manage_config')
    manage_config = PageTemplateFile('www/config', globals(),
                                     __name__='manage_config')

    def __init__(self, id, title=None):
        self._id = self.id = id
        self.title = title
        self.wikid_port = 8388
        self.wikid_host = "127.0.0.1"
        self.domaincode = '127000000001'
        self.passPhrase = 'passphrase'
        self.caCert = ''
        self.pkey = ''

    #
    #   IAuthenticationPlugin implementation
    #
    #security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):

        """ See IAuthenticationPlugin.

        o We expect the credentials to be those returned by
          ILoginPasswordExtractionPlugin.
        """
        login = credentials.get('login')
        password = credentials.get('password')

        try:
            w = pywClient(host=self.wikid_host, port=self.wikid_port,
                        pkey=self.pkey, passPhrase=self.passPhrase,
                        caCert=self.caCert)
        except:
            return None

        if login is None or password is None:
            return None
        res = w.checkCredentials(login, self.domaincode, password)
        if res is True:
            return login, login
        else:
            print None

    security.declareProtected(ManagePortal, 'manage_updateConfig')
    @postonly
    def manage_updateConfig(self, REQUEST):
        """Update configuration of Trusted Proxy Authentication Plugin.
        """
        def verify():
            msg = "Configuration Error: "

            try:
                int(wikid_port)
            except ValueError:
                return msg + "  'Port' must be an integer."
            if not os.path.exists(pkey):
                return  msg + " Cannot access to '%s' No such file." % pkey
            if not os.path.exists(caCert):
                return msg + " Cannot access to '%s' No such file." % caCert
            try:
                pywClient(host=wikid_host, port=wikid_port, pkey=pkey,
                          passPhrase=passPhrase, caCert=caCert)
            except:
                return msg + " WIKID Client error. Check certificates."

        response = REQUEST.response
        wikid_port = REQUEST.form.get('wikid_port')
        wikid_host = REQUEST.form.get('wikid_host')
        domaincode = REQUEST.form.get('domaincode')
        passPhrase = REQUEST.form.get('passPhrase')
        caCert = REQUEST.form.get('caCert')
        pkey = REQUEST.form.get('pkey')

        err = verify()
        if not err:
            self.wikid_port = int(wikid_port)
            self.wikid_host = wikid_host
            self.domaincode = domaincode
            self.passPhrase = passPhrase
            self.caCert = caCert
            self.pkey = pkey

            response.redirect('%s/manage_config?manage_tabs_message=%s' %
                              (self.absolute_url(), 'Configuration+updated.'))
        else:
            response.redirect('%s/manage_config?manage_tabs_message=%s' %
                              (self.absolute_url(),
                               err + ' Configuration+NOT+updated.'))


classImplements(WiKIDAuthPlugin, IAuthenticationPlugin)

InitializeClass(WiKIDAuthPlugin)
