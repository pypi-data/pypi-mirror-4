from Acquisition import aq_inner, aq_parent

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import base_hasattr

try:
    from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import WorkflowPolicyConfig_id
    from Products.CMFPlacefulWorkflow.interfaces.portal_placeful_workflow import IPlacefulMarker
    HAS_PLACEFUL = True
except:
    HAS_PLACEFUL = False

def get_workflow_policy(context):
    if not HAS_PLACEFUL:
        return None

    wtool = getToolByName(context, 'portal_workflow')
    if IPlacefulMarker.providedBy(wtool):
        chain = None
        current_ob = aq_inner(context)
        while current_ob is not None and not IPloneSiteRoot.providedBy(current_ob):
            if base_hasattr(current_ob, WorkflowPolicyConfig_id):
                return getattr(current_ob, WorkflowPolicyConfig_id)

            current_ob = aq_inner(aq_parent(current_ob))

    return None
