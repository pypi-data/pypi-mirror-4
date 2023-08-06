# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from rt.atmigrator import atmigratorMessageFactory as _
from rt.atmigrator import logger
from rt.atmigrator.migrator import migrateContents
from zope.component import getUtility
#Plone 3 compatibility
try:
    from zope.app.schema.vocabulary import IVocabularyFactory
except:
    from zope.schema.interfaces import IVocabularyFactory


class MigrateView(BrowserView):
    """
    A view that allows to migrate a portal-type into another
    """
    def __call__(self):
        """
        Check values in the request, and make the right action
        """
        if 'form.button.Cancel' in self.request.form.keys():
            return self.doReturn(_("migration_error_cancel",
                                   default=u"Migration canceled."), 'info')
        if not 'form.button.Migrate' in self.request.form.keys():
            return self.index()
        if not self.request.form.get('src_type', '') and not self.request.form.get('dst_type', ''):
            return self.doReturn(_("migration_error_validation",
                                   default=u"You need to fill both required fields."), 'error')
        migration = self.doMigration()
        if migration:
            return self.doReturn(_("migration_done_msg",
                                 default=u"Migration done."), 'info')
        else:
            return self.doReturn(_("migration_error_msg",
                                   default=u"Errors in migration process. See the log for more infos."), 'error')

    def doMigration(self):
        """
        handle migration from a portal_type to anther, and log all outputs given
        """
        src_type = self.request.form.get('src_type', '')
        dst_type = self.request.form.get('dst_type', '')
        logger.info("*********** Migration start ***********")
        output = migrateContents(self.context, src_type, dst_type)
        pu = getToolByName(self.context, "plone_utils")
        pu.addPortalMessage(_("Migration from ${src_type} to ${dst_type}: found ${results} items.",
                              mapping={u"src_type": src_type,
                                        "dst_type": dst_type,
                                        "results": output.get('counter', '')}),
                            'info')
        for m in output.get('msg', []):
            logger.info(m)
        logger.info("*********** Migration done ***********")
        if output.get('error', []):
            for error in output.get('error', []):
                pu.addPortalMessage(error.get('msg', ''), 'error')
                return False
        return True

    def getTypesList(self):
        """
        Return an user friendly list of portal_types
        """
        utility = getUtility(IVocabularyFactory,
                             "plone.app.vocabularies.UserFriendlyTypes")
        if utility:
            return utility(self.context)._terms

    def doReturn(self, message, type):
        """
        Add a portal message and make a redirect
        """
        pu = getToolByName(self.context, "plone_utils")
        pu.addPortalMessage(message, type=type)
        return_url = "%s/@@migrate-types" % self.context.absolute_url()
        self.request.RESPONSE.redirect(return_url)
