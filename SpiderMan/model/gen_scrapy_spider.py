import logging
from scrapy.commands.genspider import *
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import optparse
import sys
from importlib import import_module


class GenSpider(Command):
    """ Rewrite the scrapy.commands.genspider.Command module to adapt to the project
    Mandatory:
        :param project_path: scrapy path
        :param spider_name: scrapy create spider name
        :param domain:  spider domain
    Option:
        :param logfile: default None
        :param loglevel: default None
        :param nolog: default None
        :param profile: default None
        :param pidfile: default None
        :param pdb: default None
        :param list: default None
        :param edit: default None
        :param dump: default None
        :param template: default basic
        :param force: defaultNone
    """

    def run(self, **kwargs):
        all_template = ["basic", "crawl", "csvfeed", "xmlfeed"]
        sys.path.insert(0, kwargs['project_path'])
        self.settings = get_project_settings()
        self.crawler_process = CrawlerProcess(self.settings)
        opts = optparse.Values({
            'logfile': kwargs.get('logfile'), 'loglevel': kwargs.get('loglevel'), 'nolog': kwargs.get('nolog'),
            'profile': kwargs.get('profile'), 'pidfile': kwargs.get('pidfile'), 'set': [], 'pdb': kwargs.get('pdb'),
            'list': kwargs.get('list'), 'edit': kwargs.get('edit'), 'dump': kwargs.get('dump'),
            'template': 'basic' if kwargs.get('template', 'basic') not in all_template else kwargs.get('template', 'basic') , 'force': kwargs.get('force')
        })
        if opts.list:
            self._list_templates()
            return False
        if opts.dump:
            template_file = self._find_template(opts.dump)
            if template_file:
                with open(template_file, "r") as f:
                    print(f.read())
            return False
        name = kwargs['spider_name']
        domain = kwargs['domain']
        module = sanitize_module_name(name)
        if self.settings.get('BOT_NAME') == module:
            # print("Cannot create a spider with the same name as your project")
            return False

        try:
            spidercls = self.crawler_process.spider_loader.load(name)
        except KeyError:
            pass
        else:
            # if spider already exists and not --force then halt
            if not opts.force:
                return False
        template_file = self._find_template(opts.template)
        if template_file:
            self.settings['NEWSPIDER_MODULE'] = '{project_name}.spiders'.format(project_name=kwargs['project_name'])
            self.settings['BOT_NAME'] = kwargs['project_name']
            self.settings['SPIDER_MODULES'] = self.settings['NEWSPIDER_MODULE']
            self.settings['SETTINGS_MODULE'] = '{project_name}.settings'.format(project_name=kwargs['project_name'])
            self._genspider(module, name, domain, opts.template, template_file)
            # if opts.edit:
            #     self.exitcode = os.system('scrapy edit "%s"' % name)

    def _genspider(self, module, name, domain, template_name, template_file):
        """Generate the spider module, based on the given template"""
        tvars = {
            'project_name': self.settings.get('BOT_NAME'),
            'ProjectName': string_camelcase(self.settings.get('BOT_NAME')),
            'module': module,
            'name': name,
            'domain': domain,
            'classname': '%sSpider' % ''.join(s.capitalize() \
                for s in module.split('_'))
        }
        if self.settings.get('NEWSPIDER_MODULE'):
            spiders_module = import_module(self.settings['NEWSPIDER_MODULE'])
            spiders_dir = abspath(dirname(spiders_module.__file__))
        else:

            spiders_module = None
            spiders_dir = "."
        spider_file = "%s.py" % join(spiders_dir, module)
        shutil.copyfile(template_file, spider_file)
        render_templatefile(spider_file, **tvars)
        if spiders_module:
            return True


# class GenSpider_(object):
#
#     model_template = {
#         "basic": "SpiderMan/model/scrapy_template/spider.tp",
#         "crawl":"SpiderMan/model/scrapy_template/crawl.tp",
#         "csvfeed": "SpiderMan/model/scrapy_template/csvf.tp",
#         "xmlfeed": "SpiderMan/model/scrapy_template/xml.tp"
#     }
#
#     def run(self, **kwargs):
#         template = self.model_template[kwargs['template']]
#         spider_name = kwargs['spider_name']
#         Spider_name = kwargs['spider_name'].capitalize()
#         domain = kwargs['domain']
#         path =




