from templer.core.vars import var
from inigo.templer.localcommands import SubTemplate
import copy

class PortletSubTemplate(SubTemplate):


    vars = [
        var('portlet_name', 'Portlet name', default='Example Portlet'),
        var('portlet_description', 'Portlet description')
    ]

    def pre(self, command, output_dir, vars):
        super(PortletSubTemplate, self).pre(command, output_dir, vars)
        vars['portlet_classname'] = vars['portlet_name'].replace(" ", "")
        vars['portlet_interfacename'] = 'I' + vars['portlet_classname']
        vars['portlet_filename'] = vars['portlet_classname'].lower()
        vars['portlet_id'] = '%s.portlet.%s' % (vars['package_dotted_name'],
                                                vars['portlet_classname'])

class BasicPortlet(PortletSubTemplate):
    
    _template_dir = 'templates/portlet/basic'
    summary = 'Adds a basic portlet skeleton'


class NonConfigurablePortlet(PortletSubTemplate):
    _template_dir = 'templates/portlet/nonconfigurable'
    summary = 'Adds a nonconfigurable portlet skeleton'

    vars = copy.deepcopy(PortletSubTemplate.vars)
    vars.append(
        var(
            'portlet_contenttypes', 
            'Content types to automatically assign to (comma separated list)',
        )
    )
    vars.append(
        var('portlet_assignmentcolumn',
            'Column of contenttype to automatically assign this portlet to',
            default='plone.rightcolumn')
    )

    def pre(self, command, output_dir, vars):
        super(NonConfigurablePortlet, self).pre(command, output_dir, vars)
        vars['portlet_contenttype_list'] = []
        for i in vars['portlet_contenttypes'].strip().split(','):
            if i:
                vars['portlet_contenttype_list'].append(i)
