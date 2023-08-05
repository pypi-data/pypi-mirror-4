from kss.core import KSSView, kssaction

class DeptSelectView(KSSView):
    """ Class to handle dept select kss """

    @kssaction
    def changeDepartments(self, school):
        """ Change departments according to chosen school object. """

        catalog = self.context.portal_catalog
        out = '<option value="" selected="selected">(Choose One)</option>\n'

        if school:
            query = school
        else:
            query = '/'.join(self.context.getPhysicalPath())+'/'
        brains = catalog(path= {'query':query, 'depth':2}, portal_type='Division')

        for x in brains:
            out += '<option value="%s">%s</option>\n' %(x.getPath(), x.Title)

        core = self.getCommandSet('core')
        core.replaceInnerHTML('#formfield-form-division select', out)
