from templer.core.vars import var
from inigo.templer.localcommands import SubTemplate

class SchemaExtender(SubTemplate):

    _template_dir = 'templates/archetypes/schemaextender'
    summary = 'Adds an archetype schemaextender skeleton'

    vars = [
        var('schemaextender_name', 'SchemaExtender name', 
            default='Example Extender'),
    ]

    def pre(self, command, output_dir, vars):
        vars['schemaextender_class_filename'] = vars['schemaextender_name'].replace(" ", "_").lower()
        vars['schemaextender_classname'] = vars['schemaextender_name'].replace(" ", "")
