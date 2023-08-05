import re
import os
from omdox import settings
from omdox import feedback
from jinja2 import Environment

def render(source_path, build_path):
    fp = open(source_path, 'r')
    contents = fp.read()
    fp.close()
    # get the bits between the content block
    re_string = '(?P<start>{%%\s+block\s+%s\s+%%})'\
                '(?P<content>.+)'\
                '(?P<end>{%%\s+endblock\s+%%})'\
                % settings.CONTENT_BLOCK
    # get the file extention
    ext = source_path.rsplit('.')
    ext.reverse()
    try:
        ext = ext[0]
    except IndexError:
        ext = None
    # only filter html
    if ext == 'html':
        # search for it if it doesn't exist don't process and warn
        try:
            block = re.search(re_string, contents, re.M|re.S)
            block_content = block.groupdict()[settings.CONTENT_BLOCK]
            for filter in settings.FILTERS:
                f = getattr(settings, filter)
                block_content = f(block_content)
            # now rebuild the contents of the doc
            contents = '%s {%% block %s %%} %s {%% endblock %%} %s' % (
                    contents[:block.start()],
                    settings.CONTENT_BLOCK,
                    block_content,
                    contents[block.end():])
        except AttributeError:
            feedback.errors.append(
                    '[error] {%% block content %%} not found in %s'\
                    % source_path)
    # parse other files for the {{ROOT}} variable
    template = Environment.from_string(settings.JINJA_ENV, contents)
    docs_path = '%s/' % os.getcwd()
    # if ROOT is not set then set it as a relative path
    ROOT = os.path.relpath(docs_path, source_path)[:-2]
    # make sure we have a config
    try:
        config = settings.config
    except AttributeError:
        settings.config = {}
    # now render
    try:
        out = template.render(ROOT=ROOT, **settings.config)
    except TypeError:
        out = template.render(**settings.config)
    # save it
    fp = open(build_path, 'w')
    fp.write(out)
    fp.close()
