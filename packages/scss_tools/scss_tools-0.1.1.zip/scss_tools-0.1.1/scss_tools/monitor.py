import os
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SCSSHandler(FileSystemEventHandler):
    """Monitor scss files and recompile
    
    """
    
    SCSS_EXTS = ['.scss']
    
    def __init__(
        self, 
        compile_func, 
        scss_dir,
        determine_func=None, 
        config_path=None, 
        logger=None
    ):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.compile_func = compile_func
        self.scss_dir = scss_dir
        self.determine_func = determine_func
        self.config_path = config_path
        if self.config_path is not None:
            self.config_path = os.path.abspath(self.config_path)
        
    def _determine_path(self, path):
        """Determine should we recompile by file path
        
        """
        # SCSS files
        _, ext = os.path.splitext(path)
        if ext.lower() not in self.SCSS_EXTS:
            self.logger.debug('Not .SCSS file, ignore')
            return False
        # in SCSS directory
        if (
            os.path.commonprefix([os.path.abspath(self.scss_dir), 
                                  os.path.abspath(path)]) != 
            os.path.abspath(self.scss_dir)
        ):
            self.logger.debug('Not in scss_dir, ignore')
            return False
        return True
        
    def _check_recompile(self, path):
        """Check modified file and recompile if needed
        
        """
        
        if (
            self.config_path is not None and 
            self.config_path == os.path.abspath(path)
        ):
            return self.recompile()
        if self.determine_func is not None:
            if self.determine_func(path):
                return self.recompile()
        if self._determine_path(path):
            return self.recompile()
    
    def on_created(self, event):
        self.logger.info('File %s was created', event.src_path)
        self._check_recompile(event.src_path)
            
    def on_modified(self, event):
        self.logger.info('File %s was modified', event.src_path)
        self._check_recompile(event.src_path)

    def on_deleted(self, event):
        self.logger.info('File %s was deleted', event.src_path)
        self._check_recompile(event.src_path)
        
    def on_moved(self, event):
        self.logger.info('File %s was moved to %s', 
                         event.src_path, event.dest_path)
        self._check_recompile(event.dest_path)
    
    def recompile(self):
        self.compile_func()


def _compile(args, cfg=None):
    from scss_tools.compiler import SCSSCompiler
    from scss_tools.command import load_cfg
    from scss_tools.command import get_compiler_kwargs
    
    cfg = load_cfg(args)
    
    compiler_cfg = cfg['compiler']
    kwargs = get_compiler_kwargs(compiler_cfg, args)
    
    compiler = SCSSCompiler(**kwargs)
    for input_path, output_path in compiler_cfg['scss_files']:
        compiler.compile(input_path, output_path)
        
    logger = logging.getLogger(__name__)
    logger.info('Compiling finished')


def _parse_args():
    import argparse
    from scss_tools.command import add_basic_args
    
    parser = argparse.ArgumentParser(
        description='Monitor file change and compile SCSS file to CSS file')
    add_basic_args(parser)
    parser.add_argument(
        '-R', '--no-recursive', dest='recursive', action='store_false',
        default=True,
        help="Don't monitor directory recursively"
    )
    parser.add_argument(
        '-M', '--no-monitor-config', dest='monitor_config',
        action='store_false', default=True,
        help="Don't monitor change of configuration file"
    )
    args = parser.parse_args()
    
    if args.logging:
        logging.basicConfig(level=logging.INFO)
    return args


def main():
    import time
    from scss_tools.command import load_cfg
    
    args = _parse_args()
    
    def compile_func():
        logger = logging.getLogger(__name__)
        try:
            _compile(args)
        except Exception, e:
            logger.error('Failed to compile')
            logger.exception(e)
        
    compile_func()
    
    cfg = load_cfg(args)
    monitor_cfg = cfg['monitor']
    
    event_handler = SCSSHandler(
        compile_func=compile_func,
        scss_dir=monitor_cfg['scss_dir'],
        config_path=args.config if args.monitor_config else None,
    )
    observer = Observer()
    observer.schedule(
        event_handler, 
        path=monitor_cfg['scss_dir'], 
        recursive=args.recursive
    )
    # monitor the configuration file
    if args.monitor_config:
        observer.schedule(
            event_handler, 
            path=os.path.dirname(args.config), 
            recursive=False
        )
        
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    
if __name__ == '__main__':
    main()
