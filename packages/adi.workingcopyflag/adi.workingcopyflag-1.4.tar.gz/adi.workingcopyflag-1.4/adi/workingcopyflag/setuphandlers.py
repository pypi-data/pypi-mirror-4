from Products.CMFCore.utils import getToolByName
from plone.app.iterate.interfaces import IBaseline

def setFlagForObjectsWithWorkingcopy(p):
    """Check if an item has a working copy and if yes, set workingcopy-flag to true.
    """
    p_types = getToolByName(p, 'portal_types')
    catalog = getToolByName(p, 'portal_catalog')

    for p_type in p_types:
        items = catalog.searchResults(portal_type=p_type)
        for item in items:
            obj = item.getObject()
            o_id = obj.getId()
            o_title = obj.Title()
            # only  originals with a workingcopy have this interface:
            if IBaseline.providedBy(obj) == True:
                flag = obj.getField('workingcopyflag')
                flag.set(obj,True)
                obj.reindexObject()
                print "INFO adi.workingcopyflag: workingcopyflag WAS set for:", o_id

def setupVarious(context):
    portal = context.getSite()
    # The following file needs to exist in ./profiles,
    # otherwise this code will not be executed.
    if context.readDataFile('adi.workingyopyflag.marker.txt') is None:
        return

# Add additional setup code here
    setFlagForObjectsWithWorkingcopy(portal)


