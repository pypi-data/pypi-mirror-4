#!/usr/bin/python
#coding: utf-8
#file   : test_bcsh.py
#author : ning
#date   : 2012-03-05 13:05:25

import os
import sys
import time
import random
import glob
import unittest
import logging
import filecmp
import shutil
#sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/..")

ENABLE_LARGE = False
HOST_BUCKET = 'http://bs.baidu.com/pybcstest'
#HOST_BUCKET = 'http://bcs.duapp.com/pybcstest'
import pybcs

pybcs.common.init_logging(logging.root, logging.INFO)


def dir_eauals(d1, d2):
    logging.info('dir_eauals?(%s, %s)' % (d1, d2))
    def equals(dcmp):
        if dcmp.left_only or dcmp.right_only or dcmp.diff_files or dcmp.funny_files :
            return False
        for sdir in dcmp.subdirs.itervalues():
            if not equals(sdir):
                return False
        return True
    dcmp = filecmp.dircmp(d1, d2)
    return equals(dcmp)

def file_equals(f1, f2):
    logging.info('file_equals?(%s, %s)' % (f1, f2))
    return filecmp.cmp(f1, f2)

def random_name():
    return str(random.randint(1024*1024,1024*1024*1024))

def iswindows():
    return os.path.sep != '/'

if not iswindows():				############## Linux
    CMD = './tools/bcsh.py '
    cases = [						
           'test/data/1.data',
           'test/data/100K.data',
           'test/data/1M+1.data',
           'test/data/中文.data',
           #'test/data/10M.data',
           #'test/data/100M.data',
           ]
    if ENABLE_LARGE:
        cases = glob.glob('test/data/*')

    dir_cases = [
        ('test/data/xxx.folder.data/', HOST_BUCKET + '/test_folder/' ),
        ('test/data/cn.folder.data/', HOST_BUCKET + '/cn_test_folder/' ),
        ('test/data/cn2.folder.data/', HOST_BUCKET + '/cn_test_folder/' ),
    ]
else:							############## Win
    CMD = r'tools\bcsh.py '
    cases = [
           r'test\data\1.data',
           r'test\data\100K.data',
           r'test\data\1M+1.data',
           ur'test\data\中文.data'.encode('gbk'),
           ]

    dir_cases = [
        ('test\\data\\xxx.folder.data\\', HOST_BUCKET + '/test_folder/' ),
        (r'test\\data\\cn.folder.data\\', HOST_BUCKET + '/cn_test_folder/' ),
        (r'test\\data\\cn2.folder.data\\', HOST_BUCKET + '/cn_test_folder/' ),
    ]

class TestBCSH(unittest.TestCase):
    def __test_singlefile(self, local_file, args):
        tmp_name = random_name()
        remote_path = HOST_BUCKET + '/abcd/%s' % tmp_name
        local_download_file = '%s.%s.download' % (local_file, tmp_name)

        r = pybcs.system('%s upload %s %s %s ' % (CMD, local_file, remote_path, args))
        print r
        assert r == '', 'return of system is not empty'

        r = pybcs.system('%s download %s %s %s' % (CMD, remote_path, local_download_file, args))
        assert r == '', 'return of system is not empty'
        assert file_equals(local_file, local_download_file), 'file not equals %s vs %s ' % (local_file, local_download_file)

        assert(file_equals(local_file, local_download_file))
        os.remove(local_download_file)
        if iswindows(): # windows cat \n \r 会有问题
            return 
        pybcs.system('%s cat %s > %s' % (CMD, remote_path, local_download_file))
        assert (r == '')
        assert file_equals(local_file, local_download_file), 'file not equals %s vs %s ' % (local_file, local_download_file)
        os.remove(local_download_file)

    def test_singlefile(self):
        print 'test_singlefile'
        for local_file in cases:
            #不管加-r 还是不加, 都应该ok
            self.__test_singlefile(local_file, '')
            #self.__test_singlefile(local_file, '-r')

    def test_superfile(self):
        print 'test_superfile'
        for local_file in cases:
            for split in ['999k', '1M']: #, '10M', '100M']:
                tmp = random_name()
                local_download_file = '%s.%s.download.file.data' % (local_file, tmp)
                remote_path = HOST_BUCKET + '/abcd/%s' % tmp
                pybcs.system('%s  upload  %s %s -d%s' % (CMD, local_file, remote_path, split))
                pybcs.system('%s  download %s %s ' % (CMD, remote_path, local_download_file))
                assert file_equals(local_file, local_download_file), 'file not equals %s vs %s ' % (local_file, local_download_file)
                os.remove(local_download_file)

    def test_dir(self):
        print 'test_dir'

        for local_dir, remote_path in dir_cases:
            tmp = random_name()
            remote_path = remote_path.replace('folder', 'folder_'+tmp)
            local_download_dir = local_dir.replace('folder', 'folder.download_' + tmp)
            pybcs.system('%s upload -r %s %s' %(CMD, local_dir, remote_path) )

            print 'sleep 5 second, it need time'
            time.sleep(5) 

            print 'download'
            pybcs.system('%s download -r %s %s ' %(CMD, remote_path, local_download_dir) )
            assert dir_eauals(local_dir, local_download_dir), 'dir not equals %s vs %s ' % (local_dir, local_download_dir)
            #shutil.rmtree(local_download_dir)

    def _test_ls(self):#TODO
        #pybcs.system('./tools/bcsh.py upload /home/ning/soft/Understand-2.6.599-Linux-32bit.tgz http://bcs.duapp.com/pybcstest/abcd/und.tgz -d10')
        pass

if __name__ == '__main__':
    unittest.main()
    #print dir_eauals('test/data/xxx.folder.data', 'test/data/xxx2.folder.data')
    #print dir_eauals('test/data/xxx.folder.data', 'test/data/yyy.folder.data')
    #print dir_eauals('test/data/xxx.folder.data', 'test/data/yyy2.folder.data')
    #print dir_eauals('test/data/xxx.folder.data', 'test/data/yyy3.folder.data')

