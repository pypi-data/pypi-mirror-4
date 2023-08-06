from Products.CMFCore.utils import getToolByName
PROFILE = 'profile-collective.z3cform.html5widgets:default'


def common(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile(PROFILE)
