## Controller Script Python "validate_author_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state  
##bind subpath=traverse_subpath
##parameters=referer,subject,message,author=None,email=None
##title=validates the form for sending feedback

from Products.CMFPlone import PloneMessageFactory as _
plone_utils=context.plone_utils
reg_tool=context.portal_registration 

if not (subject and subject.strip()):
    state.setError('subject', _(u'Please enter a subject.'), 'email_required')

if not (message and message.strip()):
    state.setError('message', _(u'Please enter a message'), 'email_required')

if context.portal_membership.isAnonymousUser():
    try:
        captcha_verify = context.restrictedTraverse('@@captcha').verify()
    except ValueError:
        context.plone_utils.addPortalMessage(_(u"Can't send message. Please contact the site administrator"), 'error')
        context.plone_log('ERROR: seems that recaptcha is not configured')
        return state.set(status='failure')
    if not captcha_verify:
        state.setError('recaptcha', _(u'Wrong captcha code provided'), 'email_required') # Ignored
    if not email:
        state.setError('email', _(u'Please submit an email address.'), 'sender_from_address_required')
    else:
        if reg_tool.isValidEmail(email):
            pass
        else:
            state.setError('email', _(u'You entered an invalid email address.'), 'invalid_email')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
