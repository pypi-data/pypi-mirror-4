import os

from paste.script import templates, copydir

class Template(templates.Template):
    summary = 'Fanstatic package'
    _template_dir = 'template_metadata'

    vars = [
        templates.var('library_name',
                      "Name of the wrapped library, like 'jQuery'"),
        templates.var('library_version',
                      "Version of the wrapped library, like '1.4.4'"),
        templates.var('library_url',
                      "URL of the wrapped library, like 'http://www.jquery.com'")]

    def pre(self, command, output_dir, vars):
        vars['project'] = vars['project'].lower()
        vars['project_stars'] = '*'*len(vars['project'])
        vars['library_name_lower'] = vars['library_name'].replace(' ', '_').lower()
        steps = vars['steps'] = vars['project'].split('.')
        vars['first_step'] = vars['steps'][0]
        if len(steps) > 1:
            vars['namespace_packages'] = "namespace_packages=['%s']," % steps[0]
        vars['steps_concat'] = ', '.join(["'%s'" % step for step in vars['steps']])
        vars['project_path'] = '/'.join(vars['steps'])

    def post(self, command, output_dir, vars):
        # Create directories for arbitrarily number of segments in the project name.
        project = vars['project']
        next_dir = output_dir
        for segment in project.split('.'):
            next_dir = os.path.join(next_dir, segment)
            os.mkdir(next_dir)
            open(os.path.join(next_dir, '__init__.py'), 'w').write(
                '''__import__('pkg_resources').declare_namespace(__name__)''')

        # We have reached the last dir.
        # (Yes, re-write __init__.py)
        template_code_dir = os.path.join(self.module_dir(), 'template_code')
        # from self.write_files:
        copydir.copy_dir(template_code_dir, next_dir,
                         vars,
                         verbosity=command.verbose,
                         simulate=False,
                         indent=1,
                         use_cheetah=self.use_cheetah,
                         template_renderer=self.template_renderer)
