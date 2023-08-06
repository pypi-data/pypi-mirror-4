from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NewsImage(ViewletBase):

    template = ViewPageTemplateFile('image.pt')

    def render(self):
        return self.template()

    def get_image(self):
        context = self.context.aq_explicit
        if context.getImage():
            scale = context.restrictedTraverse('@@images')
            return scale.scale(
                'image',
                width=300,
                height=300).tag()
        return u''