#!/usr/bin/python
#coding: utf-8
#file   : bcsh.py
#author : ning
#date   : 2012-03-02 13:00:51


# 功能:
# upload
# download
# ls
# cat
# 支持superfile
# 重点在于支持superfile, 目录, retry 的上传功能
# 其他(create_bucket, del_bucket, set_acl等)请到yun.baidu.com设置



import urllib, urllib2, httplib
import os, re, sys, time
import logging, glob, argparse
import hmac, base64, hashlib, commands
from urlparse import urlparse
import ConfigParser

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/..")

import pybcs 
from pybcs.common import parse_size, format_time, format_size

__VERSION__ = '1.2'
MAX_PART_CNT = 1024
  
def iswindows():
    return os.path.sep != '/'

import time

def retry(ExceptionToCheck, tries=4, delay=2, backoff=2, #logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        excpetions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param #logger: #logger to use. If None, print
    :type #logger: logging.Logger instance
    """
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            try_one_last_time = True
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                    try_one_last_time = False
                    break
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if #logger:
                        #logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if try_one_last_time:
                return f(*args, **kwargs)
            return
        return f_retry  # true decorator
    return deco_retry

def parse_bcs_location(bcs_url):
    '''parset location like http://bcs.duapp.com/bucket/object '''
    if not bcs_url:
        b, o = (None, None)
    elif len(bcs_url) <= 1:
        b, o = (None, None)
    else:
        path = urlparse(bcs_url).path
        path = re.sub(r'//', '/', path)
        path = path[1:]

        sp = path.split('/', 1)
        if (len(sp) == 1):
            b, o = (sp[0], None)
        else:
            b, o = (sp[0], '/'+sp[1])
    logging.debug('parse_bcs_location(%s): [%s][%s]' % (bcs_url, b, o))
    return b, o

def __upload_with_superfile(bcs, src, dst, split):
    ''' 用superfile 方式上传 '''
    logging.info('__upload_with_superfile(%s, %s, %d)' % (src, dst, split))
    b, o = parse_bcs_location(dst)
    bucket = bcs.bucket(b)
    filesize = os.path.getsize(src) 
    if filesize % split == 0:
        parts_cnt = filesize/split
    else:
        parts_cnt = filesize/split + 1

    if parts_cnt >= MAX_PART_CNT:
        logging.error('error: too many sub objects(%d>%d) use larger split size please' %(parts_cnt, MAX_PART_CNT))
        return
    superfile_parts = []

    for partid in range(parts_cnt):
        start = partid * split
        if start + split < filesize:
            length = split
        else:
            length = filesize - start
        sub_o = bucket.object('%s.part%d' % (o, partid))
        sub_o.put_file_part(src, start, length)
        superfile_parts.append(sub_o)

    sup = bucket.superfile(o, superfile_parts)
    sup.put()

@retry(Exception, tries=3)
def __upload(bcs, src, dst, split):
    if iswindows():
        dst = dst.decode('gbk').encode('utf8')

    filesize = os.path.getsize(src) 
    if (filesize > split):
        return __upload_with_superfile(bcs, src, dst, split)
    else:
        b, o = parse_bcs_location(dst)
        bucket = bcs.bucket(b)
        bucket.object(o).put_file(src)

@retry(Exception, tries=3)
def __download(bcs_object, local_path):
    bcs_object.get_to_file(local_path)

def __upload_dry(bcs, src, dst):
    print '%s > %s' % (src, dst)

IGNORE_LST = ['.']
def ignore(filename):
    for i in IGNORE_LST:
        if filename.startswith(i):
            return True
    return False
    #return filename.startswith('.')

def list_files(path):
    lst = []
    try:
        iter = os.walk(path, followlinks=True)
    except TypeError: # python 2.5 does not support followlinks
        iter = os.walk(path)

    for root, dirs, files in iter:
        ignore_dirs = [i for i in dirs if ignore(i)]
        for i in ignore_dirs:
            dirs.remove(i)

        ignore_files = [i for i in dirs if ignore(i)]
        for i in ignore_files:
            files.remove(i)

        lst.extend([os.path.join(root, f) for f in files])
    return lst 

def upload(bcs, src, dst, recursive, split):
    """docstring for upload"""
    if os.path.isdir(src): src_type = 'dir' 
    else : src_type = 'file' 

    if dst.endswith('/'): dst_type = 'dir' 
    else : dst_type = 'file' 
        
    if src_type!= dst_type:
        print 'not match!, "%s" is <%s> but "%s" is <%s>' % (src, src_type, dst, dst_type)
        return 

    if os.path.isdir(src) and not recursive:
        print "omitting directory '%s', use -r for dir upload" % src
        return

    if not os.path.exists(src): #not exists
        print '%s not exists' % src
        return

    if not os.path.isdir(src): #one file
        __upload(bcs, src, dst, split)
        return

    if  os.path.isdir(src) and (not src.endswith(os.path.sep)):
        src = src+os.path.sep
    #upload dir
    upload_lst = []
    for f in list_files(src):
        t = f.replace(src, '')  # src=/home/ f=/home/ab, after replace, we got : ab
                                # dst=bs://bucket/dir/
        #print f, dst, t
        t2 = os.path.join(dst, t)
        t2 = t2.replace('\\', '/') #for win
        upload_lst.append((f, t2))
    for (s, d) in upload_lst:
        __upload(bcs, s, d, split)

def get_remote_list_raw(bcs, bcs_url):
    LIMIT =100
    b, o = parse_bcs_location(bcs_url)
    bucket = bcs.bucket(b)
    start = 0
    while True:
        lst = bucket.list_objects_raw(o, start=start, limit=LIMIT)

        if len(lst) == 0: break
        start += len(lst)
        for obj_json in lst:
            obj = bucket.object(obj_json['object'].encode('utf8'))
            obj_json['full_path'] = str(obj)
            yield obj_json

def get_remote_list(bcs, bcs_url):
    LIMIT =100
    b, o = parse_bcs_location(bcs_url)
    bucket = bcs.bucket(b)
    start = 0
    while True:
        lst = bucket.list_objects(o, start=start, limit=LIMIT)
        if len(lst) == 0: break
        start += len(lst)
        for obj in lst:
            yield obj

def download(bcs, remote_path, local_path, recursive):
    """download http://bcs.duapp.com/b/o afile 

        download -r http://bcs.duapp.com/b/dir adir : 

            http://bcs.duapp.com/b/dir -> adir
            http://bcs.duapp.com/b/dir/file1 -> adir/file1
            http://bcs.duapp.com/b/dir/folder1 -> adir/folder1
    """


    #非递归，直接下载单个文件即可, 如果不存在直接报错.
    if not recursive:
        b, o = parse_bcs_location(remote_path)
        bucket = bcs.bucket(b)
        assert not remote_path.endswith('/'), 'no recursive remote_path should not endswith /'
        assert not local_path.endswith(os.path.sep), ('no recursive remote_path should not endswith %s' % os.path.sep)
        bucket.object(o).get_to_file(local_path)
        return

    if not remote_path.endswith('/'):
        print 'with -r , remote_path should be a dir and  endswith "/" ' 
        return
    if not local_path.endswith(os.path.sep):
        print 'with -r , local_path should endswith "%s"' % os.path.sep
        return

    lst = list( get_remote_list(bcs, remote_path) )

    if len(lst) == 0 : 
       print 'src is empty'
       return

    if os.path.exists(local_path) and os.listdir(local_path):
        print 'target dir already exist and not empty!, it it dangerous, choose another dir'
        return

    for item in lst:
        item_remote_path = str(item)
        logging.debug('abc %s | %s | %s' % (local_path, item_remote_path, remote_path) )
        logging.debug('gen local_path %s & %s' % (local_path, item_remote_path[len(remote_path):]) )
        item_local_path = os.path.join(local_path, item_remote_path[len(remote_path):])
        if iswindows():
            item_local_path = item_local_path.replace('/', os.path.sep).decode('utf8').encode('gbk')
        logging.info('get %s -> %s' % (item_remote_path, item_local_path) )
        item_local_dir = os.path.dirname(item_local_path)
        if not os.path.exists(item_local_dir):
            logging.info('mkdirs %s' % item_local_dir )
            os.makedirs(item_local_dir)

        try:
            __download(item, item_local_path)
        except:
            logging.warn('ignored %s on download' % str(item))
            pass
            

def cat(bcs, src):
    """docstring for download"""
    b, o = parse_bcs_location(src)
    bucket = bcs.bucket(b)
    body = bucket.object(o).get()['body'] 
    sys.stdout.write(body)

def __rm(bcs_object):
    bcs_object.delete()

def __rm_dry(bcs_object):
    print 'rm ', bcs_object


def rm(bcs, remote_path, recursive):
    for item in get_remote_list(bcs, remote_path):
        __rm(item)

def ls(bcs, bcs_url, detail):
    '''list bucket '''
    #if (not bcs_url) or ('http://bcs.duapp.com/'.startswith(bcs_url) ): # no bcs_url or root
        #for b in bcs.list_buckets():
            #print b
        #return
    b, o = parse_bcs_location(bcs_url)
    if not b:
        for b in bcs.list_buckets():
            print b
        return

    def print_item(item):
        if item['is_dir']:
            item['permission'] = 'drwx------'
            item['size'] = 0
        else:
            item['permission'] = '-rwx------'

        item['mdatetime'] =  format_time(item['mdatetime'])
        if detail: 
            fmt = '%(permission)-10s %(size)-10d %(mdatetime)s %(full_path)s' 
        else:
            fmt = '%(full_path)s' 
        print fmt % item

    for item in get_remote_list_raw(bcs, bcs_url):
        print_item(item)

def get_config_path():
    return os.path.expanduser('~/.bcsh')

def auth(ak, sk, bcs_host):

    config = ConfigParser.RawConfigParser()
    config.add_section('bcs')
    config.set('bcs', 'AK', ak)
    config.set('bcs', 'SK', sk)
    config.set('bcs', 'BCS_HOST', bcs_host)

    cfg_file = get_config_path()
    logging.info('write ak[%s] sk[%s] to %s' % (ak, sk, cfg_file))
    configfile = open(cfg_file, 'wb')
    config.write(configfile)
    configfile.close()

def load_cfg(args):
    cfg_file = get_config_path()
    config = ConfigParser.ConfigParser()
    cfg = config.read(cfg_file)

    args.AK = config.get('bcs', 'AK')
    args.SK = config.get('bcs', 'SK')
    if config.get('bcs', 'BCS_HOST'):
        args.BCS_HOST = config.get('bcs', 'BCS_HOST')

    logging.info('get ak, sk from :%s , ak[%s], sk[%s]' % (cfg_file, args.AK, args.SK) )


def _init_logging(args):
    if not args.verbose :
        pybcs.init_logging(logging.WARN)
        logging.root.setLevel(logging.WARN)
    if args.verbose == 1:
        pybcs.init_logging(logging.INFO)
        logging.root.setLevel(logging.INFO)
    if args.verbose == 2:
        pybcs.init_logging(logging.DEBUG)
        logging.root.setLevel(logging.DEBUG)

    logging.info(args)

def main(args):
    if (args.op == 'auth'):
        auth(args.AK, args.SK, args.BCS_HOST)

    try:
        load_cfg(args)
        bcs = pybcs.BCS(args.BCS_HOST, args.AK, args.SK, pybcs.PyCurlHTTPC)
    except :
        print '''no ak, sk in %s, run bcsh auth --AK=xxx --SK=xxx ''' % get_config_path()
        return

    if (args.op == 'ls'):
        ls(bcs, args.bcs_url, args.detail)
    elif (args.op == 'cat'):
        cat(bcs, args.src)
    elif (args.op == 'download'):
        download(bcs, args.src, args.dst, args.recursive)
    elif (args.op == 'upload'):
        if (args.dry_run):
            global __upload, __upload_dry
            __upload = __upload_dry # replace it
        args.split = parse_size(args.split)
        upload(bcs, args.src, args.dst, args.recursive, args.split)

    elif (args.op == 'rm'):
        if (args.dry_run):
            global __rm, __rm_dry
            __rm = __rm_dry # replace it
        rm(bcs, args.remote_path, args.recursive)

if __name__ == "__main__":
    parser_shared = argparse.ArgumentParser(add_help=False)
    parser_shared.add_argument('-v', '--verbose', action='count',
                        help="verbose") 

    parser = argparse.ArgumentParser(parents=[parser_shared])
    parser.add_argument('--version', action='version', version=__VERSION__,
                        help='Print the version and exit')

    subparsers = parser.add_subparsers(dest="op",
        help='sub-command help')


    ## the parser for the "auth" command
    parser_auth = subparsers.add_parser('auth', parents=[parser_shared], help='auth ak, sk ')

    parser_auth.add_argument('--AK', help='ak of bcs. ')
    parser_auth.add_argument('--SK', help='sk of bcs. ')
    parser_auth.add_argument('--BCS-HOST', default='http://bcs.duapp.com/',
                             help='set bcs host , "http://bcs.duapp.com/" ')

    ## the parser for the "ls" command
    parser_ls = subparsers.add_parser('ls', parents=[parser_shared], help='list all object start with remote_path')

    parser_ls.add_argument('-l', '--list', action='store_true', dest='detail',
                           help='use a long listing format (show detail) ')

    parser_ls.add_argument('bcs_url', help='remote path', nargs='?')

    ## the parser for the "upload" command
    parser_upload = subparsers.add_parser('upload', parents=[parser_shared], help='upload local file/dir to bcs ')
    parser_upload.add_argument('-r', '-R', '--recursive', action='store_true' ,
                               help='upload directories recursively')
    parser_upload.add_argument('src', help='local dir / file')
    parser_upload.add_argument('dst', help='remote path')

    parser_upload.add_argument('-u', '--dry-run', action='store_true' ,
                               help='do not actually do anything, only for upload')
    parser_upload.add_argument('-d', '--split', default='1G', # default 1G
                               help='split size on put largefiles with superfile, example : -d 1M -d 100M, default: 1G')

    ## the parser for the "download" command
    parser_download = subparsers.add_parser('download', parents=[parser_shared], help='download remote file(s) to local')
    parser_download.add_argument('-r', '-R', '--recursive', action='store_true' ,
                               help='download directories recursively')
    parser_download.add_argument('src', help='remote path')
    parser_download.add_argument('dst', help='local dir/file')

    ## the parser for the "rm" command
    parser_rm= subparsers.add_parser('rm', parents=[parser_shared], 
                                     help="delete all object start with remote_path, "
                                         "just like `rm remote_path* -rf`")
    parser_rm.add_argument('-r', '-R', '--recursive', action='store_true' ,
                           help='rm all object start with `remote_path`')
    parser_rm.add_argument('remote_path', help='remote path')

    parser_rm.add_argument('-u', '--dry-run', action='store_true' ,
                               help='do not actually do anything, just show command')

    ## the parser for the "cat" command
    parser_cat = subparsers.add_parser('cat', parents=[parser_shared], help='cat remote file content')
    parser_cat.add_argument('src', help='remote path')

    args = parser.parse_args()
    _init_logging(args)

    main(args)

