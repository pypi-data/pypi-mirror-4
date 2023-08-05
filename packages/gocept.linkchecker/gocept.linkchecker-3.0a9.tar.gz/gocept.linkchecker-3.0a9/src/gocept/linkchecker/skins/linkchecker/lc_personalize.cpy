## Controller Python Script "personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=lc_notify_details=[], lc_notify_frequency=[], lc_notify_changes_only=0
##title=Personalization Handler.

from Products.CMFPlone import transaction_note

member=context.portal_membership.getAuthenticatedMember()
member.setProperties(context.REQUEST)

tmsg=member.getUserName()+' personalized their link monitoring settings.'
transaction_note(tmsg)

return state.set(portal_status_message='Your link monitoring settings have been saved.')
