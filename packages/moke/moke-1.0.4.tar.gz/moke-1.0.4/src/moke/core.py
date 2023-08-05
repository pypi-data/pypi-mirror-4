"""
:mod:`moke.core`
================

``moke`` is not like ``make``. The core package provides the ``task`` the
``task`` all in one decorator.

"""

__all__ = ["MokeError", "task", "stdin", "stdout", "stderr", "num", "doc",
           "INFO", "WARN", "ERROR"]
__version__ = "1.0.4"


import os
import sys
import inspect
import logging
from re import search
from itertools import izip_longest
from argparse import ArgumentParser, FileType
from types import TypeType
from types import FileType as BaseFileType
from ConfigParser import SafeConfigParser

# do not remove, really
from logging import INFO, WARN, ERROR #@UnusedImport
from sys import stdin, stdout, stderr #@UnusedImport


__defcfg__ = "/dev/null"

__deflog__ = {"ls":stderr, # log stream
              "ll":"info", # log level
              "lf":"tab", # log format
             }

__logforms__ = {"tab":"%(asctime)s\t%(message)s"
                }

nan = float("nan")
devnull = open(os.devnull, "wb")

# monkey patching now to have simpler code later
file_w = FileType("wb")
file_w.__dict__["__name__"] = "file_w"
file_r = FileType("rb")
file_r.__dict__["__name__"] = "file_r"
file_a = FileType("a+")
file_a.__dict__["__name__"] = "file_a"

# automatic import of mokelib

class MokeError(Exception):
    """General moke exception.
    """
    pass

def num(x):
    """(internal) check if value is a number.
    """
    try:
        num = int(x)
    except ValueError:
        try:
            num = float(x)
        except:
            num = nan
    return num

def doc(docstring):
    """Decorator that attaches a docstring to a function.
    
      - docstring(``str``) some documentation
    
    """
    def docwrapper(func):
        func.__doc__ = docstring
        return func

    return docwrapper


class task(object):
    """Decorator that creates an argparse subcommand from a function.
    """
    
    __funcs = {}

    @staticmethod
    def _makecfg(args):
        cfg = args.pop("config")
        parser = SafeConfigParser()
        parser.readfp(cfg)
        return parser

    @staticmethod
    def _makelgr(args, cfg):
        # default arguments
        defargs = {"level":__deflog__["ll"],
                   "stream":__deflog__["ls"],
                   "format":__deflog__["lf"]
                   }
        # config file arguments
        cfgargs = {}
        if cfg.has_section("log"):
            for name in ("level", "stream", "format"):
                if cfg.has_option("log", name):
                    value = cfg.get("log", name)
                    # manual type corrections
                    if name in ("stream",):
                        value = open(value, "a+")
                    cfgargs[name] = value
                else:
                    cfgargs[name] = None
        # command line arguments
        # these are set to defaults by argparse
        linargs = {"level":args.pop("ll"),
                   "stream":args.pop("ls"),
                   "format":args.pop("lf")
                   }
        finargs = {}
        for key in ("level", "stream", "format"):
            # default
            finargs[key] = defargs[key]
            # config if set
            if cfgargs[key]:
                finargs[key] = cfgargs[key]
            # linargs if set
            if linargs[key] != defargs[key]:
                finargs[key] = linargs[key]
        # prepare options
        logstream = finargs["stream"]
        loglevel = getattr(logging, finargs["level"].upper())
        logformat = __logforms__[finargs["format"]]
        # make logger
        lgr = logging.getLogger("moke")
        lgr.setLevel(loglevel)
        sh = logging.StreamHandler(stream=logstream)
        sh.setFormatter(logging.Formatter(logformat))
        lgr.addHandler(sh)
        return lgr

    @staticmethod
    def _parsetype(line):
        # parses (sometypeX) or (``sometypeX``),
        # where X is a number or ? + * (argparse nargs)
        try:
            sometype, nargs = search("\(`{0,2}([a-z_]*)([\?\+\*]{1}|[0-9]?)`{0,2}\)",
                                     line).groups()
        except AttributeError:
            return None
        # test if sometype is a known type
        try:
            sometype = eval(sometype)
        except (NameError, SyntaxError):
            return None
        if not (issubclass(type(sometype), TypeType) or \
                isinstance(sometype, FileType) or sometype is num):
            return None
        # fix empty string
        nargs = nargs or None
        if nargs not in ('+', '?', '*', None):
            try:
                nargs = int(nargs)
            except ValueError:
                return None
        return sometype, nargs

    @classmethod
    def _parsearg(cls, doclines, arg):
        docline, argtype, nargs = "", str, None # defaults
        # the space is mandatory for rst compatibility
        arg_type = "- " + arg + "(" # with type
        arg_noty = "- " + arg + " " # without type
        for line in doclines:
            if (arg_type in line or arg_noty in line) and line.startswith("-"):
                try:
                    docline = line.replace("-", "", 1).replace(arg, "", 1).strip()
                    argtype, nargs = cls._parsetype(line)
                except TypeError:
                        pass
                break # only the first match
        return docline, argtype, nargs

    @classmethod
    def _funcparse(cls):
        # parses gathered functions
        main_parser = ArgumentParser()

        # global options
        main_parser.add_argument("-config", type=file_r, default=__defcfg__, 
                                 help="(file_r) [default: None] configuration file")
        
        main_parser.add_argument("-ls", type=file_a,
            default=__deflog__["ls"],
            help="(file_a) [default: %s] logging stream" % __deflog__["ls"].name)

        main_parser.add_argument("-ll", type=str,
            default=__deflog__["ll"], choices=("info", "warn", "error"),
            help="(str) [default: %s] logging level" % __deflog__["ll"])

        main_parser.add_argument("-lf", type=str,
            default=__deflog__["lf"], choices=("tab",),
            help="(str) [default: %s] logging format" % __deflog__["lf"])
        
        # subcommand options
        sub_parsers = None
        for name, func in cls.__funcs.iteritems():
            args, varargs, varkwargs, defaults = inspect.getargspec(func)
            if varargs or varkwargs:
                raise MokeError("*args and **kwargs not supported in tasks")
            arglines = []
            doclines = []
            if func.__doc__ and func.__doc__.strip():
                for l in func.__doc__.splitlines():
                    l = l.strip()
                    if l.startswith("-"):
                        arglines.append(l)
                    elif l:
                        doclines.append(l)
            if name == "main":
                task_parser = main_parser
                task_parser.description = "\n".join(doclines)
            else:
                if not sub_parsers:
                    sub_parsers = main_parser.add_subparsers()
                task_parser = sub_parsers.add_parser(name, help="\n".join(doclines))
            
            task_parser.set_defaults(func = func)
            if defaults:
                ldef = len(defaults)
                required = args[:-ldef]
                optional = args[-ldef:]
            else:
                required = args
                optional = ()
                defaults = ()
            
            for arg, deft in izip_longest(optional, defaults):
                docline, argtype, nargs = cls._parsearg(arglines, arg)
                if deft is False:
                    if not docline:
                        docline = "(switch) [default: OFF]"
                    task_parser.add_argument("--" + arg, action="store_true",
                                             default=deft, help=docline)
                elif deft is True:
                    if not docline:
                        docline = "(switch) [default: ON]"
                    task_parser.add_argument("--" + arg, action="store_false",
                                                 default=deft, help=docline)
                else:
                    # function signature > docs string
                    if deft is not None:
                        argtype = type(deft)
                    if argtype is BaseFileType:
                        # stdin, stdout or an open file
                        argtype = eval("file_" + deft.mode[0])

                    # default = most types
                    argname = argtype.__name__
                    argrepr = getattr(deft, "name", str(deft))
                    argdoc = "(%s) [default: %s] " % (argname, \
                                                argrepr.replace("%", "%%"))
                    if docline:
                        # (XXX) [default: YYY] CONTENT, (XXX) CONTENT, CONTENT
                        argdoc += docline.split(")")[-1].split("]")[-1].strip()
                    task_parser.add_argument("-" + arg, type=argtype, \
                                        nargs=nargs, default=deft, help=argdoc)
            for arg in required:
                docline, argtype, nargs = cls._parsearg(arglines, arg)
                argdoc = "(%s) " % argtype.__name__
                if docline:
                    argdoc += docline.split(")")[-1].split("]")[-1].strip()
                else:
                    argdoc += "a required positional argument"
                task_parser.add_argument(arg, type=argtype, nargs=nargs, \
                                         help=argdoc)
        return main_parser

    @classmethod
    def _callfunc(cls, args):
        # get function and logger
        func = args.pop("func")
        cfg = cls._makecfg(args)
        lgr = cls._makelgr(args, cfg)
        # where are we?
        cwd = os.getcwd()
        mokefile = os.path.abspath(os.path.join(cwd, sys.argv[0]))
        # remember default and command line args
        names, _, _, defs = inspect.getargspec(func)
        defs = (defs or ()) # defs can be None
        diff = len(names) - len(defs)

        vals = []
        for i, name in enumerate(names):
            try:
                vals.append(args[name])
            except KeyError:
                vals.append(defs[i - diff])

        params = " ".join(\
                [str(tpl) for tpl in zip(names, vals)])

        # write logging header
        msgs = ("moke (version %s)" % __version__,
                "cwd: \"%s\"" % cwd,
                "mokefile: \"%s\"" % mokefile,
                "task: %s" % func.func_name,
                "params: %s" % params)
        for msg in msgs:
            lgr.info(msg)
        # final call, leaving moke
        return func(**args)

    @classmethod
    def _call(cls):
        # calls the selected function with the parsed arguments
        parser = cls._funcparse()
        try:
            args = dict(parser.parse_args().__dict__)
        except Exception:
            return 1
        retval = cls._callfunc(args) # modifies args
        return retval

    def __init__(self, func=None):

        # gather functions or call selected sub-command
        if inspect.isfunction(func):
            self.__name = func.__name__
            self.__funcs[self.__name] = func
        elif self.__funcs:
            # file contains some functions
            self._call()

    def __call__(self, *args, **kwargs):
        return self.__funcs[self.__name](*args, **kwargs)
