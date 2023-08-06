from nose.plugins.base import Plugin

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine


def alembic_attr(*args, **kwargs):
    """Decorator that adds attributes to classes or functions
    for use with the Attribute (-a) plugin.
    """

    def wrap_ob(ob):
        for name in args:
            setattr(ob, name, True)
        for name, value in kwargs.iteritems():
            setattr(ob, name, value)
        return ob

    return wrap_ob


def get_method_attr(method, cls, attr_name, default=False):
    """Look up an attribute on a method/ function.
    If the attribute isn't found there, looking it up in the
    method's class, if any.
    """
    Missing = object()
    value = getattr(method, attr_name, Missing)
    if value is Missing and cls is not None:
        value = getattr(cls, attr_name, Missing)
    if value is Missing:
        return default
    return value


class AlembicAttrib(Plugin):
    """Selects test cases to be run if the current database migration version is sufficiently upgraded.
    """

    def options(self, parser, env):
        """Register command line options"""
        super(AlembicAttrib, self).options(parser, env)
        parser.add_option("--alembic-ini",
                          dest="ini", action="store",
                          help="Location of alembic.ini file")
        parser.add_option("--alembic-echo",
                          dest="echo", action="store",
                          help="Turn sqlalchemy engine echo on")

    def configure(self, options, config):
        super(AlembicAttrib, self).configure(options, config)

        ini = options.ini if options.ini else "alembic.ini"
        echo = True if options.echo else False

        config = Config(ini)
        url = config.get_main_option("sqlalchemy.url")
        engine = create_engine(url, echo=echo)
        connection = engine.connect()
        context = MigrationContext.configure(connection)
        script = ScriptDirectory.from_config(config)

        self.current_revision = context.get_current_revision()
        self.revisions = [script.revision for script in script.iterate_revisions(self.current_revision, None)]

    def validateRevision(self, method, cls=None):
        """
        If the annotated revision is less than or equal to the current revision, return true
        """
        minimum_revision = get_method_attr(method, cls, 'minimum_revision')
        if not minimum_revision:
            return None

        return minimum_revision in self.revisions

    def wantFunction(self, function):
        """Accept the function if its attributes match.
        """
        return self.validateRevision(function)

    def wantMethod(self, method):
        """Accept the method if its attributes match.
        """
        try:
            cls = method.im_class
        except AttributeError:
            return False
        return self.validateRevision(method, cls)
