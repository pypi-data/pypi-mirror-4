from Products.CMFCore.utils import getToolByName
from plone.app.iterate.relation import WorkingCopyRelation
from plone.app.iterate.interfaces import IBaseline

def setFlag(obj, event):
    """Sets workingcopyflag to true, when the item has been checked-in.
    """
    flag = obj.getField('workingcopyflag')
    flag.set(obj,True)
    obj.reindexObject()

def removeFlag(obj, event):
    """Sets workingcopyflag to false, when the item has been checked-out.
    """
    flag = obj.getField('workingcopyflag')
    flag.set(obj,False)
    obj.reindexObject()

def removeFlagOnCancel(obj, event):
    """ Sets workingcopyflag to false on original item, when cancelling.
    """
    # get the original item of the copy:
    relations = obj.getRefs(WorkingCopyRelation.relationship)
    for relation in relations:
        # let's make sure we have a workingcopy-relation, 
        # and not another kind of rel:
        if IBaseline.providedBy(relation):
            flag = relation.getField('workingcopyflag')
            flag.set(relation,False)
            relation.reindexObject()

