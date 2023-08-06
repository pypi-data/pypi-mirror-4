from Products.CMFCore.utils import getToolByName


def v18(context):
    context.runImportStepFromProfile('profile-Products.cooptation:default',
                                     'workflow',
                                     run_dependencies=False,
                                     purge_old=False)
    wtool = getToolByName(context, "portal_workflow")
    portal_cooptations = getToolByName(context, "portal_cooptations")
    w = wtool.getWorkflowsFor(portal_cooptations)[0]
    w.updateRoleMappingsFor(portal_cooptations)
    portal_cooptations.reindexObjectSecurity()
