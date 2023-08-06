from zope import interface
from zope.formlib import form
from plone.app.form.base import EditForm
from plone.app.form.validators import null_validator
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from quintagroup.silogroup import silogroupMessageFactory as _


class ISiloNavigationSchema(interface.Interface):
    # -*- extra stuff goes here -*-
    pass


class SiloNavigation(EditForm):
    form_fields = form.FormFields(ISiloNavigationSchema)
    label = _(u'Silo Navigation')
    template = ViewPageTemplateFile('silo_navigation_form.pt')

    @form.action(_(u"label_save", default=u"Save"), name=u'save')
    def handle_save_action(self, action, data):
        contents = self.context.getFolderContents()
        menu_ids = self.request.get('menu_ids', self.context.objectIds())
        for i in contents:
            obj = i.getObject()
            setattr(obj, 'exclude_from_nav', not i.id in menu_ids)
            setattr(obj, 'silo', self.request.get(i.id+'_title', ''))
            obj.reindexObject(['exclude_from_nav', 'silo'])

    @form.action(_(u"label_cancel", default=u"Cancel"),
                 validator=null_validator, name=u'cancel')
    def handle_cancel_action(self, action, data):
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)
