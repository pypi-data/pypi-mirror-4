from Products.CMFCore.utils import getToolByName


def v2(context):
    context.runImportStepFromProfile('profile-collective.js.fullcalendar:default',
                                     'jsregistry', run_dependencies=False,
                                     purge_old=False)
    getToolByName(context, 'portal_javascripts').cookResources()


def v3(context):
    context.runImportStepFromProfile('profile-collective.js.fullcalendar:default',
                                     'cssregistry', run_dependencies=False,
                                     purge_old=False)
    getToolByName(context, 'portal_css').cookResources()


def recook_js_resources(context):
    getToolByName(context, 'portal_javascripts').cookResources()

