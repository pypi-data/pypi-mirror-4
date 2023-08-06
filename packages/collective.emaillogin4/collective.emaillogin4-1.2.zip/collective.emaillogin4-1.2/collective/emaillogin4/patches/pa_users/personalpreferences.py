from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from zope.formlib.interfaces import WidgetInputError

from plone.app.users.browser.personalpreferences import UserDataPanel
from plone.app.users.browser.personalpreferences import UserDataPanelAdapter


def get_email(self):
    # This is the same as original, but we need to override both the
    # setter and the getter.
    return self._getProperty('email')


def set_email(self, value):
    if value is None:
        value = ''
    props = getToolByName(self, 'portal_properties').site_properties
    if props.getProperty('use_email_as_login'):
        mt = getToolByName(self.context, 'portal_membership')
        if self.context.getId() == mt.getAuthenticatedMember().getId():
            set_own_login_name(self.context, value)
        else:
            pas = getToolByName(self.context, 'acl_users')
            pas.updateLoginName(self.context.getId(), value)
    return self.context.setMemberProperties({'email': value})


def validate(self, action, data):
    context = aq_inner(self.context)
    errors = super(UserDataPanel, self).validate(action, data)

    if not self.widgets['email'].error():
        props = getToolByName(context, 'portal_properties')
        if props.site_properties.getProperty('use_email_as_login'):
            # Keeping your email the same (which happens when you
            # change something else on the personalize form) or
            # changing it back to your original user id, is fine.
            membership = getToolByName(context, 'portal_membership')
            if self.userid:
                member = membership.getMemberById(self.userid)
            else:
                member = membership.getAuthenticatedMember()
            email = data['email']
            pas = getToolByName(context, 'acl_users')
            email = pas.applyTransform(email)
            if email not in (member.getId(), member.getUserName()):
                # Our email has changed and is not the same as our
                # user id or login name, so we need to check if
                # this email is already in use by another user.
                pas = getToolByName(context, 'acl_users')
                if (membership.getMemberById(email) or
                        pas.searchUsers(name=email, exact_match=True)):
                    err_str = _(
                        'message_email_in_use',
                        default=(
                            u"The email address you selected is "
                            u"already in use or is not valid as login "
                            u"name. Please choose another."))
                    errors.append(WidgetInputError(
                            'email', u'label_email', err_str))
                    self.widgets['email'].error = err_str

    return errors

# Patch it.
UserDataPanel.validate = validate
UserDataPanelAdapter.get_email = get_email
UserDataPanelAdapter.set_email = set_email
UserDataPanelAdapter.email = property(get_email, set_email)

# We may be too late with patching set_own_login_name in CMFPlone, as
# p.a.users may have imported the original function already.
from collective.emaillogin4.patches.cmfplone.utils import set_own_login_name
import plone.app.users.browser.personalpreferences
plone.app.users.browser.personalpreferences.set_own_login_name = set_own_login_name
