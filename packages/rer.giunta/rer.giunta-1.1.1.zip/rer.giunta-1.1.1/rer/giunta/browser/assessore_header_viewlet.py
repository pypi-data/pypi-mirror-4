from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName

class AssessoreViewletBase(ViewletBase):
    index = ViewPageTemplateFile('assessore_header_viewlet.pt')

    def __init__(self, context, request, view, manager):
        super(AssessoreViewletBase, self).__init__(context, request, view, manager)
        self.assessore=self.getAssessoreObj()
        self.assessore_elements=self.getAssessoreElements()
        
    def render(self):
        if self.assessore:
            return self.index()
        else:
            return ""
    
    def getAssessoreObj(self):
        if self.context.portal_factory.isTemporary(self.context):
            return None
        if self.request.ACTUAL_URL.endswith('/atct_edit') or self.request.ACTUAL_URL.endswith('/edit'):
            return None
        for elem in self.context.aq_inner.aq_chain:
            if getattr(elem,'portal_type','') == "RERAssessore":
                return elem
        return None
    
    def getAssessoreElements(self):
        """
        """
        if not self.assessore:
            return []
        pc=getToolByName(self.context,'portal_catalog')
        return pc(path={"query":'/'.join(self.assessore.getPhysicalPath()),"depth":1},
                  sort_on='getObjPositionInParent',
                  is_folderish=True)
    
    def getSelectedTab(self):
        assessore_elements_uids=[x.UID for x in self.assessore_elements]
        if self.context != self.assessore:
            for elem in self.context.aq_inner.aq_chain:
                if getattr(elem,'UID',''):
                    if elem.UID() in assessore_elements_uids:
                        return elem.getId()
        tab=self.request.form.get('tab','')
        if not tab:
            return "biography"
        else:
            return tab 