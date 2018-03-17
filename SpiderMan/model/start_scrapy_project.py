# -*- coding:utf-8 -*-
from scrapy.commands.startproject import *
from scrapy.utils.project import inside_project, get_project_settings


class StartScrapyProject(Command):

    def run(self, project_name, project_dir, opts=None):
        """ Rewrite the scrapy scrapy.commands.startproject.Command module to adapt to the project
        ：
        :param project_dir: scrapy project path
        :param project_name: scrapy project name
        :param opts: {
            'logfile': None, 'loglevel': None,
             'nolog': None, 'profile': None,
             'pidfile': None, 'set': [], 'pdb': None
             }
        :return: bool
        """
        self.settings = get_project_settings()
        if opts is None:
            opts = {
                'logfile': None, 'loglevel': None,
                'nolog': None, 'profile': None,
                'pidfile': None, 'set': [], 'pdb': None
            }

        if not self._is_valid_name(project_name):
            self.exitcode = 1
            return False

        self._copytree(self.templates_dir, abspath(project_dir))
        move(join(project_dir, 'module'), join(project_dir, project_name))
        for paths in TEMPLATES_TO_RENDER:
            path = join(*paths)
            tplfile = join(project_dir,
                           string.Template(path).substitute(project_name=project_name))
            render_templatefile(tplfile, project_name=project_name,
                                ProjectName=string_camelcase(project_name))
        return True
