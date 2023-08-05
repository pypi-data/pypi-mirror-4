from zope.component import queryUtility
from plone.app.discussion.interfaces import ICaptcha
from plone.registry.interfaces import IRegistry
from plone.app.discussion.browser.validator import CaptchaValidator
from plone.app.discussion.interfaces import IDiscussionSettings
from Products.CMFCore.utils import getToolByName
from plone.z3cform.fieldsets import extensible
from z3c.form import form, field, button
from plone.app.discussion.interfaces import IComment
from Products.statusmessages.interfaces import IStatusMessage
from cs.commenteditor import commenteditorMessageFactory as _

class EditForm(extensible.ExtensibleForm, form.Form):
    ignoreContext = False # use context to get widget data
    id = None
    label = _(u"Edit this comment")
    fields = field.Fields(IComment).omit('portal_type',
                                         '__parent__',
                                         '__name__',
                                         'comment_id',
                                         'mime_type',
                                         'creation_date',
                                         'modification_date',                                         
                                         'title',
                                         'in_reply_to',
                                         )

    @button.buttonAndHandler(_(u"edit_comment_button", default=u"Edit Comment"),
                             name='comment')
    def handleComment(self, action):
        # Validation form
        data, errors = self.extractData()
        if errors:
            return

        # Validate Captcha
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        portal_membership = getToolByName(self.context, 'portal_membership')
        if settings.captcha != 'disabled' and \
        settings.anonymous_comments and \
        portal_membership.isAnonymousUser():
            if not 'captcha' in data:
                data['captcha'] = u""
            captcha = CaptchaValidator(self.context,
                                       self.request,
                                       None,
                                       ICaptcha['captcha'],
                                       None)
            captcha.validate(data['captcha'])

        for k,v in data.items():
            setattr(self.context, k, v)

        IStatusMessage(self.request).addStatusMessage(_(u'The message was edited successfuly'))
        self.request.response.redirect(self.context.absolute_url())