import os
import re
import shutil
import walkdir
import hashlib
import yaml
from omdox import settings
from omdox import feedback
from omdox.render import render


class Tree:
    '''The Tree represents the hierarchy of the documentation'''
    _branches = []
    _branch_data = {}
    _root = None

    def __init__(self, *args, **kwargs):
        self._root = args[0]
        self._grow()

    @property
    def root(self):
        return self._root

    def get_branches(self):
        return self._branches

    def add_branch(self, branch):
        return self._branches.append(branch)


    def _grow(self):
        '''finds all available branches for tree'''
        for dir in walkdir.filtered_walk(
                self._root,
                excluded_dirs=[settings.BUILD_DIR]):
            # add the branch
            branch = Branch(dir[0], self.root)
            # add the nodes
            nodes = dir[-1]
            for filename in nodes:
                ext = os.path.splitext(filename)[-1]
                # ignores
                if filename in settings.EXCLUDED:
                    continue
                # now build the nodes
                if filename in settings.UTILITY_NODES:
                    node = UtilityNode(branch, filename)
                elif ext in settings.EXTENTIONS:
                    node = DocNode(branch, filename)
                else:
                    node = StaticNode(branch, filename)
                branch.add_node(node)
            # now add the branch
            self.add_branch(branch)
    

class Branch:

    def __init__(self, *args, **kwargs):
        self._nodes = []
        self._path = args[0]
        self._root = args[1]
        self._name = os.path.relpath(self._path, self._root)

    def __repr__(self):
        return '<Branch %s>' %  self.src_path()

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def root(self):
        return self._root

    def get_nodes(self):
        return self._nodes

    def add_node(self, node):
        self._nodes.append(node)
        return node

    def src_path(self):
        return os.path.join(self._root)

    def build_path(self):
        return os.path.join(
            self.root,
            settings.BUILD_DIR,
            self._name)

    def process(self):
        '''if the path doesn't exist in the _build dir then
        make it'''
        if not os.path.exists(self.build_path()):
            feedback.header(
                    '[creating folder] %s' % self.name)
            os.makedirs(self.build_path())

class BaseNode:
    '''A base node used for inheriting'''


    def __init__(self, *args, **kwargs):
        # set the branch
        self.branch = args[0]
        # set the filename
        self.filename = args[1]
        # build the checksum
        self.last_known_checksum = self.checksum()

    def __repr__(self):
        return '%s' % self.src_path()


    def name(self):
        '''return the filename'''
        return u'%s' % self.filename

    def src_path(self):
        return os.path.join(self.branch.path, self.filename)

    def build_path(self):
        return os.path.join(
                self.branch.root,
                settings.BUILD_DIR,
                self.branch._name,
                self.filename)

    def process(self):
        raise NotImplementedError(
                'process method is not implemented in BaseNode class')

    def has_changed(self):
        checksum = self.checksum()
        if self.last_known_checksum != checksum:
            feedback.header(
                '[changed] %s/%s' % (
                    self.branch.name,
                    self.filename))
            self.last_known_checksum = checksum
            return True
        return False
        

    def checksum(self):
        try:
            with open(self.src_path(), 'r') as fp:
                md5 = hashlib.md5()
                while True:
                    data = fp.read(2**20)
                    if not data:
                        break
                    md5.update(data)
            return md5.hexdigest()
        except IOError:
            return self.last_known_checksum


class UtilityNode(BaseNode):
    ''' Utilility nodes are for files that play a role in the docs
    but are not part of the final build - layout.html, config.yaml'''
    UTILITY = True

    def __repr__(self):
        return '<UtilityNode %s>' % self.src_path()

    def process(self):
        '''reload the config'''
        del(settings.config)
        try:
            stream = open('%s/config.yaml' % os.getcwd(), 'r')
            config = yaml.load(stream)
            stream.close()
            setattr(settings, 'config', {})
            for key, value in config.items():
                settings.config[key] = value
        except (AttributeError, IOError):
            config = {}
        if config is None:
            setattr(settings, 'config', {})



class DocNode(BaseNode):
    ''' Doc nodes are for documentation that is to be parsed'''
    DOC = True

    def __repr__(self):
        return '<DocNode %s>' % self.src_path()

    def process(self):
        '''render the file out'''
        feedback.header(
                '[rendering] %s/%s' % (
                    self.branch.name,
                    self.filename))
        render(self.src_path(), self.build_path())

    def name(self):
        '''read the title from the block title'''
        if 'html' in self.filename:
            f = open(self.src_path())
            contents = f.read()
            re_string = '{%%\s+block\s+%s\s+%%}'\
                        '(?P<title>.+?)'\
                        '{%%\s+endblock\s+%%}'\
                        % settings.TITLE_BLOCK
            try:
                title_re = re.search(re_string, contents, re.M|re.S)
                title = title_re.groupdict()[settings.TITLE_BLOCK]
            except AttributeError:
                title = self.filename
            return title
        else:
            return self.filename

class StaticNode(BaseNode):
    ''' Static nodes are for static files (js,css,img etc) that
    is to be copied into place'''
    STATIC = True


    def __repr__(self):
        return '<StaticNode %s>' % self.src_path()

    def process(self):
        '''move to the build folder'''
        feedback.header(
                '[copying] %s/%s' % (
                    self.branch.name,
                    self.filename))
        shutil.copyfile(self.src_path(), self.build_path())


