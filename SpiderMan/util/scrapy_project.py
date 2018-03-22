# -*- coding:utf-8 -*-
import re
import os
import sys
import time

import subprocess
from unipath import path



def file_exist(file_path):
    """check file is exist
    :type file_path: file abs path
    :return bool file not exist return False else return True
    """
    count = 0
    while 1:
        if os.path.exists(file_path):
            return True
        if count >= 300:
            return False
        count += 1
        time.sleep(0.01)


def delete_scrapy_project(file_path, project_name):
    """delete location scrapy project
    :param file_path: scrapy project path
    :return: bool
    """
    try:
        path_object = path.Path(os.path.join(file_path, project_name))
        path_object.rmtree(project_name)
        return True
    except:
        import traceback
        traceback.print_exc()
        return False


# def create_scrapy_project(project_name, spider_name, spider_url, base_project, SPIDER_MAN_SCRAPY_FILE_PATH):
#     all_apider_model = {"basic", "crawl", "csvfeed", "xmlfeed"}
#     os.makedirs(os.path.join(SPIDER_MAN_SCRAPY_FILE_PATH, project_name, spider_name, 'spiders'))
#     with open(os.path.join(SPIDER_MAN_SCRAPY_FILE_PATH, project_name, 'scrapy.cfg'), 'w') as f:
#         f.write(SCRAPY_CFG.format(project_name=project_name))


# def build_scrapy_object(project_name, spider_name, spider_url, base_project, SPIDER_MAN_SCRAPY_FILE_PATH):
#     """new scrapy object
#     basic, crawl, csvfeed, xmlfeed
#     :param SPIDER_MAN_SCRAPY_FILE_PATH: wenjian 路径
#     :param project_name: scrapy project name
#     :param spider_name: scrapy spider anme. scrapy crawl spider_name
#     :param spider_url: scrapy spider url
#     :return: bool or project path
#     """
#
#
#
#
#
#     if project_name not in os.listdir(SPIDER_MAN_SCRAPY_FILE_PATH):
#         p2 = subprocess.Popen(
#             ["scrapy", "startproject", "{project_name}".format(project_name=project_name)],
#             shell=True, cwd=SPIDER_MAN_SCRAPY_FILE_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE
#         )
#         if 'scrapy <command>' in p2.stdout.read().deocde():
#             subprocess.Popen(
#                 ["scrapy startproject {project_name}".format(project_name=project_name)],
#                 shell=True, cwd=SPIDER_MAN_SCRAPY_FILE_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE
#             )
#
#     if file_exist(os.path.join(SPIDER_MAN_SCRAPY_FILE_PATH, project_name)) is False:
#         return False
#     p2 = subprocess.Popen(
#         [
#             "scrapy", "genspider", "-t", "{base_project}".format(
#             base_project="basic" if base_project not in all_apider_model else base_project
#         ),
#             "{spider_name}".format(spider_name=spider_name), spider_url
#         ],
#         shell=True, cwd=os.path.join(SPIDER_MAN_SCRAPY_FILE_PATH, project_name),
#         stdout=subprocess.PIPE, stderr=subprocess.PIPE
#     )
#     if 'scrapy <command>' in p2.stdout.read().deocde():
#         subprocess.Popen(
#             [
#                 "scrapy genspider -t {base_project}".format(
#                 base_project="basic" if base_project not in all_apider_model else base_project
#             ),
#                 "{spider_name}".format(spider_name=spider_name), spider_url
#             ],
#             shell=True, cwd=os.path.join(SPIDER_MAN_SCRAPY_FILE_PATH, project_name),
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE
#         )
#     return os.path.join(SPIDER_MAN_SCRAPY_FILE_PATH, project_name)


def build_egg(project_path, name, version, SCRAPY_SETUP_CODE):
    """Package scrapy project
    :param SCRAPY_SETUP_CODE:
    :param project_path: scrapy project path
    :param name: scrapy name
    :param version: scrapyd version
    :param setting_model: scrapyd model.setting
    :return: egg file path
    """
    if not os.path.isdir(project_path):
        return False
    with open(os.path.join(project_path, 'setup.py'), 'w', encoding='utf-8') as f:
        f.write(SCRAPY_SETUP_CODE % {"name": name, "version": str(version)})
    if file_exist(project_path) is False:
        return False
    p2 = subprocess.Popen(
        [
            sys.executable, 'setup.py', 'bdist_egg'
        ],
        shell=True, cwd=project_path,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    egg_file = ''.join(re.findall(r"creating 'dist\\(\S+)'", p2.stdout.read().decode()))

    if not file_exist(os.path.join(project_path, 'dist')):
        return False
    return os.path.join(project_path, 'dist', egg_file)


def scrapy_file(path):
    """scrapy file path
    :param path: scrapy project path
    :return: scrapy path
    """
    spider_name = path.split(os.sep)[-1]
    project_path = os.path.join(path, spider_name)
    if not os.path.isdir(project_path):
        return False
    data = []
    for i in os.listdir(project_path):
        if os.path.isdir(os.path.join(project_path, i)):
            for l in os.listdir(os.path.join(project_path, i)):
                if '__init__' not in l and 'pyc' not in l and '__pycache__' not in l:
                    data.append(os.path.join(os.path.join(project_path, i), l))
        elif "__init__" not in i and 'pyc' not in i and os.path.isfile(os.path.join(project_path, i)):
            data.append(os.path.join(project_path, i))
    return data
