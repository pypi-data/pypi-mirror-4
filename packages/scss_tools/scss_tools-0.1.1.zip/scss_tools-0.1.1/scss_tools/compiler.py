import logging

import scss
from scss import config


class SCSSCompiler(object):
    
    def __init__(
        self, 
        load_paths, 
        static_root, 
        asset_root, 
        verbosity=0,
        compress=True,
        debug_info=False,
        logger=None
    ):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        #: SCSS import path
        self.load_paths = load_paths
        #: Static root path (Where images and static resources are located)
        self.static_root = static_root
        #: Assets root path (Sprite images will be created here)
        self.asset_root = asset_root
        #: verbosity of SCSS compiler
        self.verbosity = verbosity
        #: compress output CSS or not
        self.compress = compress
        #: display debug information or not
        self.debug_info = debug_info
        
        self.logger.info('Create SCSS compiler')
        self.logger.info('VERBOSITY=%r', self.verbosity)
        self.logger.info('LOAD_PATHS=%r', self.load_paths)
        self.logger.info('STATIC_ROOT=%r', self.static_root)
        self.logger.info('ASSETS_ROOT=%r', self.asset_root)
        self.logger.info('Compress=%r', self.compress)
        self.logger.info('debug_info=%r', self.debug_info)
        
    def compile(self, input_path, output_path):
        """Compile SCSS file into CSS file, input_path is the path to SCSS file 
        to compile, output_path is the path to output CSS file
        
        """
        # NOTICE: SCSS compiler use the evil global variables, it's not thread
        # safe here
        config.VERBOSITY = self.verbosity
        config.LOAD_PATHS = ','.join(self.load_paths)
        config.STATIC_ROOT = self.static_root
        config.ASSETS_ROOT = self.asset_root
        s = scss.Scss(scss_opts={
            'compress': self.compress,
            'debug_info': self.debug_info,
        })
        self.logger.info('Compiling %s to %s...', input_path, output_path)
        with open(input_path, 'rt') as file_:
            content = file_.read() 
        result = s.compile(content)
        with open(output_path, 'wt') as file_:
            file_.write(result)
        self.logger.info('Finished compiling %r to %r', input_path, output_path)


def _parse_args():
    import argparse
    from scss_tools.command import add_basic_args
    
    parser = argparse.ArgumentParser(
        description='Compile SCSS file to CSS file')
    add_basic_args(parser)
    args = parser.parse_args()
    
    if args.logging:
        logging.basicConfig(level=logging.INFO)
    return args


def main():
    from scss_tools.command import load_cfg
    from scss_tools.command import get_compiler_kwargs
    
    args = _parse_args()
    cfg = load_cfg(args)
    
    compiler_cfg = cfg['compiler']
    kwargs = get_compiler_kwargs(compiler_cfg, args)
    
    compiler = SCSSCompiler(**kwargs)
    for input_path, output_path in compiler_cfg['scss_files']:
        compiler.compile(input_path, output_path)

if __name__ == '__main__':
    main()
