import os
import re
import json
import string
import logging
from datetime import datetime

import pkg_resources
from webhelpers.html import literal

from . import errors
from .core import widget_context
from .utils import push_context, LazyProperty

DEFAULT_TEMPLATE_ENGINE='core-ew'

log = logging.getLogger(__name__)

class _Renderer(object):

    def __init__(self, text='', engine=None, *args, **kwargs):
        if engine is None: engine = DEFAULT_TEMPLATE_ENGINE
        self._text = text
        self._engine = engine
        self._args = args
        self._kwargs = kwargs

    def __call__(self, context):
        template = self.template
        for k,v in self._kwargs.items():
            setattr(template, k, v)
        return self.engine.render(self.template, context)

    @LazyProperty
    def engine(self):
        return TemplateEngine.get_engine(self._engine)

    @LazyProperty
    def template(self): # pragma no cover
        raise NotImplementedError, 'template'

class Snippet(_Renderer):
    @LazyProperty
    def template(self):
        return self.engine.parse(self._text)
        
class File(_Renderer):
    @property
    def template(self):
        '''the template object for the file

        This should not be a LazyProperty because we want to let the loader
        decide whether or not to reload the file.
        '''
        return self.engine.load(self._text, *self._args, **self._kwargs)

class TemplateEngine(object):
    _engines = None
    variable_providers = []

    def __init__(self, entry_point, config):
        self.name = entry_point.name
        self.config = config

    @classmethod
    def initialize(cls, config):
        cls._engines = {}
        for ep in pkg_resources.iter_entry_points('easy_widgets.engines'):
            log.debug('Loading template engine %s', ep.name)
            config_prefix = ep.name + '.'
            ep_config = dict(
                (k[len(config_prefix):], v)
                for k,v in config.iteritems()
                if k.startswith(config_prefix))
            try:
                cls._engines[ep.name] = ep.load()(ep, ep_config)
            except errors.EngineNotFound: # pragma no cover
                log.debug('Error loading engine %s', ep.name)
            except:
                log.exception('Error loading engine %s', ep.name)

    @classmethod
    def get_engine(cls, name):
        if cls._engines is None:
            cls.initialize({})
        return cls._engines.get(name)

    @classmethod
    def register_variable_provider(cls, provider):
        '''Plugin point to allow functions to manipulate the context
        passed to *all* templates for *all* widgets.

        def provider(context): ...

        TemplateEngine.register_variable_provider(provider)
        '''
        cls.variable_providers.append(provider)

    def load(self, template_name, **kwargs): # pragma no cover
        raise NotImplementedError, 'load'

    def parse(self, template_text): # pragma no cover
        raise NotImplementedError, 'parse'

    def render(self, template, context): # pragma no cover
        raise NotImplementedError, 'load'

    def context(self, user_context):
        context = dict(
            widget=widget_context.widget)
        for provider in self.variable_providers:
            provider(context)
        context.update(user_context)
        return context

class JsonEngine(TemplateEngine):
    def _default_json(obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        elif isinstance(obj, datetime):
            return obj.isoformat(' ')
        raise TypeError(repr(obj) + " is not JSON serializable")
    encoder=json.JSONEncoder(default=_default_json)
    
    def load(self, template_name, **kwargs):  # pragma no cover
        return None

    def parse(self, template_text, filepath=None):
        return None

    def render(self, template, context):
        return self.encoder.encode(context)

class CoreEngine(TemplateEngine):
    '''Simple extension of string.Template allowing for expressions in ${...}'''

    class ExprDict(dict):
        re_escape = re.compile(r'&|<|>')

        def get(self, k, *args):
            try:
                return self[k]
            except KeyError:
                if args: return args[0]
                raise

        def __getitem__(self, k):
            try:
                return eval(k, dict(self))
            except KeyError:
                raise
            except Exception, ex:
                return '[Exception in %s: %s]' % (k, ex)

    class ExprTemplate(string.Template):
        idpattern = r'[_a-z][^}]*'

    def __init__(self, entry_point, config):
        super(CoreEngine, self).__init__(entry_point, config)
        self._dotted_filename_finder = _DottedFilenameFinder()

    def load(self, template_name, **kwargs):
        try:
            filepath = self._dotted_filename_finder.get_dotted_filename(
                template_name, template_extension='.html')
            return self.parse(open(filepath).read(), filepath)
        except IOError:
            raise errors.TemplateNotFound, '%s not found at %s' % (
                template_name, filepath)

    def parse(self, template_text, filepath=None):
        return self.ExprTemplate(unicode(template_text))

    def render(self, template, context):
        context = self.context(context)
        context = self.ExprDict(context)
        return literal(template.safe_substitute(context))

class Jinja2Engine(TemplateEngine):

    def __init__(self, entry_point, config):
        try:
            import jinja2
        except ImportError: # pragma no cover
            raise errors.EngineNotFound, 'jinja2'
        self.jinja2 = jinja2
        super(Jinja2Engine, self).__init__(entry_point, config)
        self._dotted_filename_finder = _DottedFilenameFinder()
        class Loader(jinja2.BaseLoader):
            def get_source(self_, environment, template):
                return self.get_source(template)
        self._environ=jinja2.Environment(
            loader=Loader(),
            **config)

    def get_source(self, template_name):
        filepath = self._dotted_filename_finder.get_dotted_filename(
            template_name, template_extension='.html')
        if not os.path.exists(filepath):
            raise self.jinja2.TemplateNotFound(template_name)
        mtime = os.path.getmtime(filepath)
        with open(filepath) as fp:
            source = fp.read().decode('utf-8')
        return source, filepath, lambda: mtime==os.path.getmtime(filepath)

    def load(self, template_name, **kwargs):
        try:
            return self._environ.get_template(template_name)
        except self.jinja2.TemplateNotFound:
            raise errors.TemplateNotFound, '%s not found' % template_name

    def parse(self, template_text, filepath=None):
        return self._environ.from_string(template_text)

    def render(self, template, context):
        context = self.context(context)
        with push_context(widget_context, render_context=context):
            text = template.render(**context)
            return literal(text)

class GenshiEngine(TemplateEngine):

    def __init__(self, entry_point, config):
        try:
            import genshi.template
        except ImportError:  # pragma no cover
            raise errors.EngineNotFound, 'genshi'
        self.genshi = genshi
        super(GenshiEngine, self).__init__(entry_point, config)
        self._dotted_filename_finder = _DottedFilenameFinder()
        self._loader = self.genshi.template.TemplateLoader(
            auto_reload=config.get('auto_reload', True),
            max_cache_size=config.get('max_cache_size', 100)
            )
        self.mode = config.get('mode', 'html')

    def load(self, template_name, **kwargs):
        try:
            filepath = self._dotted_filename_finder.get_dotted_filename(
                template_name, template_extension='.html')
            return self._loader.load(filepath)
        except self.genshi.template.TemplateNotFound:
            raise errors.TemplateNotFound, '%s not found at %s' % (
                template_name, filepath)

    def parse(self, template_text, filepath=None):
        return self.genshi.template.MarkupTemplate(
            template_text,
            filepath=filepath,
            loader=self._loader)

    def render(self, template, context):
        context = self.context(context)
        with push_context(widget_context, render_context=context):
            stream = template.generate(**context)
            text = stream.render(self.mode)
            text = unicode(text, 'utf-8')
            return literal(text)

class KajikiEngine(TemplateEngine):
    force_mode=None

    def __init__(self, entry_point, config):
        try:
            import kajiki
        except ImportError: # pragma no cover
            raise errors.EngineNotFound, 'kajiki'
        super(KajikiEngine, self).__init__(entry_point, config)
        self.kajiki = kajiki
        self._loader = kajiki.PackageLoader(
            reload=config.get('reload', True),
            force_mode=config.get('force_mode', self.force_mode),
            )

    def load(self, template_name, *args, **kwargs):
        kwargs.setdefault('is_fragment', True)
        try:
            return self._loader.load(template_name, *args, **kwargs)
        except IOError:
            raise errors.TemplateNotFound, template_name

    def parse(self, template_text, filepath=None, **kwargs):
        kwargs.setdefault('is_fragment', True)
        if self.force_mode is None:
            return self.kajiki.XMLTemplate(
                template_text,
                filename=filepath,
                **kwargs)
        else:
            return self.kajiki.XMLTemplate(
                template_text,
                filename=filepath,
                mode=self.force_mode,
                **kwargs)

    def render(self, template, context):
        context = self.context(context)
        with push_context(widget_context, render_context=context):
            return literal(template(context).render())

class KajikiTextEngine(KajikiEngine):
    force_mode='text'

    def parse(self, template_text, filepath=None):
        return self.kajiki.TextTemplate(
            template_text,
            filename=filepath)

class KajikiHTML4Engine(KajikiEngine):
    force_mode='html'

class KajikiHTML5Engine(KajikiEngine):
    force_mode='html5'

class KajikiXMLEngine(KajikiEngine):
    force_mode='xml'

class _DottedFilenameFinder(object):

    def __init__(self):
        self.cache = {}

    def get_dotted_filename(self, name, template_extension):
        result = self.cache.get(name, None)
        if result is not None: return result
        package, template = name.rsplit('.', 1)
        basename = template + template_extension
        try:
            result = pkg_resources.resource_filename(package, basename)
        except ImportError, e:
            e.args = (
                e.args[0]
                + '. Perhaps you have forgotten an __init__.py in that folder.',)
            raise
        self.cache[name] = result
        return result

