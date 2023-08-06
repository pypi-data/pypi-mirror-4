from plone.app.layout.viewlets import content
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

class NewsByline(content.DocumentBylineViewlet):

    template = ViewPageTemplateFile('byline.pt')

    def render(self):
        return self.template()

    def update(self):
        super(NewsByline, self).update()
        self.plone_tools = getMultiAdapter(
            (self.context, self.request),
            name='plone_tools')
        
    def creator(self):
        userid = self.context.Creator()
        mt = getToolByName(self.context, 'portal_membership')
        member = mt.getMemberById(userid)
        if member:
            return member.getProperty('fullname') or userid
        return userid

    def getWorkflowState(self):
        state = self.context_state.workflow_state()
        workflows = self.plone_tools.workflow().getWorkflowsFor(self.context)
        if workflows:
            for w in workflows:
                if state in w.states:
                    return w.states[state].title or state

    def show_state(self):
        """Show viewlet, depends on available workflow transitions"""
        # default - copied from plone.app.layout.viewlets.content
        properties = getToolByName(self.context, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        available = not self.anonymous
        has_transitions = len(self.plone_tools.workflow() \
            .getTransitionsFor(self.context))
        return (available and has_transitions)
