# import filters into this namespace
import os
from omdox.filters import *
from jinja2 import Environment, FileSystemLoader, Template
import yaml
# 
try:
    stream = open('%s/config.yaml' % os.getcwd(), 'r')
    config = yaml.load(stream)
    stream.close()
    if config is None:
        config = {}
except IOError:
    config = {}

# set up the defaults
# the name of the title block 
try:
    TITLE_BLOCK = config['TITLE_BLOCK']
except (TypeError, KeyError):
    TITLE_BLOCK = 'title'
try:
    NAV_IGNORE_DIRS = config['NAV_IGNORE_DIRS']
except (TypeError, KeyError):
    NAV_IGNORE_DIRS = ['img', 'css', 'js']
# the name of the build dir
try:
    BUILD_DIR = config['BUILD_DIR']
except (TypeError, KeyError):
    BUILD_DIR = '_build'
# exclude these directories and files
try:
    EXCLUDED = config['EXCLUDED']
except (TypeError, KeyError):
    EXCLUDED = (
        '_build',
        '.sass-cache',
        '.DS_Store',
        'conf.py',
        'conf.pyc',
    )
# utility nodes
try:
    UTILITY_NODES = config['UTILITY_NODES']
except (TypeError, KeyError):
    UTILITY_NODES = (
        'layout.html',
        'config.yaml',
    )
# which extentions to render?
try:
    EXTENTIONS = config['EXTENTIONS']
except (TypeError, KeyError):
    EXTENTIONS = (
        '.html',
        '.css',
    )
# the blocks to parse for code and markdown
try:
    CONTENT_BLOCK = config['CONTENT_BLOCK']
except (TypeError, KeyError):
    CONTENT_BLOCK = 'content'
# exclude these files
try:
    FILTERS = config['FILTERS']
except (TypeError, KeyError):
    FILTERS = (
       'pygmentize',
       'markdown',
    )
# the root for urls and paths - forward slash essential
try:
    ROOT = config['ROOT']
except (TypeError, KeyError):
    ROOT = '/'
JINJA_ENV = Environment( loader=FileSystemLoader('.'))
