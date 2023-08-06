import os
import logging

import yaml


truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))


def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is any of ``t``, ``true``, ``y``, ``on``, or ``1``, otherwise
    return the boolean value ``False``.  If ``s`` is the value ``None``,
    return ``False``.  If ``s`` is already one of the boolean values ``True``
    or ``False``, return it."""
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy


def get_pkg_dir():
    """Get scss_tools package directory
    
    """
    import scss_tools
    pkg_dir = os.path.dirname(scss_tools.__file__)
    return pkg_dir


def get_scss_dir():
    """Get SCSS directory in this package
    
    """
    pkg_dir = get_pkg_dir()
    return os.path.join(pkg_dir, 'scss')


def add_basic_args(parser):
    parser.add_argument(
        '-c', '--config', dest='config', action='store',
        default='scss.yaml',
        help='path/to/scss-config.yaml'
    )
    parser.add_argument(
        '-L', '--no-logging', dest='logging', action='store_false',
        default=True,
        help='not to logging messages'
    )


def load_cfg(args):
    logger = logging.getLogger(__name__)
    logger.info('Loading configuration from %r ...', args.config)
    with open(args.config, 'rt') as file_:
        cfg = yaml.load(file_)
    return cfg


def get_compiler_kwargs(cfg, args):
    """Get kwargs for compiler by configuration and arguments
    
    """    
    kwargs = {}

    def add_arg(key, default=None, arg_key=None):
        if key in cfg:
            kwargs[key or arg_key] = cfg[key]
        else:
            if default is None:
                raise KeyError('%s must be set in configuration')
            kwargs[key or arg_key] = default
    
    add_arg('static_root', os.curdir)
    add_arg('asset_root', os.curdir)
    add_arg('load_paths', [])
    add_arg('compress', True)
    add_arg('debug_info', False)
    add_arg('verbosity', 0)
    
    kwargs['compress'] = asbool(kwargs['compress'])
    kwargs['debug_info'] = asbool(kwargs['debug_info'])
    
    if asbool(cfg.get('use_buildin_scss', True)):
        kwargs['load_paths'].insert(0, get_scss_dir())
    return kwargs
