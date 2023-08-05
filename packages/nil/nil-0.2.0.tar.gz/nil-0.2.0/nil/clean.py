#coding:utf-8

import os
import shutil
import fnmatch

def all_file(root, patterns='*.pyc', ignore_dirs=[], \
        single_level=False, logger=None, no_matchs=False):
    """
    root:            需要遍历的目录
    patterns：       需要查找的文件，以, 为分割的字符串
    single_level:    是否只遍历单层目录，默认为否
    """
    patterns = tuple([p.strip() for p in patterns.split(',')])
    ignore_dirs = set(ignore_dirs)
    for path, subdirs, files in os.walk(root):
        has_ignore_dirs = set(subdirs) & ignore_dirs
        if has_ignore_dirs:
            subdirs[:] = [d for d in subdirs if not d in has_ignore_dirs]
        for pattern in patterns:
            fs = fnmatch.filter(files, pattern)
            ds = fnmatch.filter(subdirs, pattern)
            if ds:
                for d in ds:
                    subdirs.remove(d)
                fs = fs + ds
            if not fs:
                if no_matchs: log('no match files in %s' % path, logger)
                continue
            for name in fs:
                yield os.path.join(path, name)
        if single_level:
            break

def log(msg, logger=None):
    if logger:
        logger.debug(msg)
    else:
        print msg

def clean(args, logger=None, no_matchs=False):
    filter = args.filter
    ignore_dirs = []
    if args.ignore_dirs:
        ignore_dirs = args.ignore_dirs.split(',')
    path = args.path
    for f in all_file(path, filter, ignore_dirs, logger=logger, \
            no_matchs=no_matchs):
        log(f, logger)
        try:
            path = os.path.realpath(f)
            if not os.path.isdir(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
        except Exception, e:
            pass

def main():
    import gc
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Clean your files.')
    parser.add_argument('path', default='.', nargs='?',
                      help="clean path")
    parser.add_argument('--filter', default='*.pyc',
                      help="fliter which file split by ,")
    parser.add_argument('--ignore-dirs', default='',
                      help="ignore some dirs split by ,")
    args = parser.parse_args()
    gc.disable()
    clean(args)
    gc.enable()
