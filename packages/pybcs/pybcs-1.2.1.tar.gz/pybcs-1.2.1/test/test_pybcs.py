#!/usr/bin/python                                                               
#coding:utf-8
#author : ning

import os
import sys,time
import hashlib
import random
import unittest
import logging

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/..")

import pybcs
#pybcs.init_logging(logging.ERROR, True, log_file_path=None)
pybcs.init_logging(logging.INFO, True, log_file_path=None)
#pybcs.init_logging(logging.DEBUG, True, log_file_path=None)

HOST = 'http://bcs.duapp.com' 

AK = os.environ['AK']           #请改为你的AK
SK = os.environ['SK']         #请改为你的SK
BUCKET = 'pybcstest'
USER = 'idning1986'

ENABLE_LARGE = False


common_header_list = set([
    'content-length',
    'accept-ranges',
    'x-bs-meta-crc32',
    'etag',
    'content-type',
    #'last-modified',
    #'expires',
])

def assert_headers(r1, r2, header_list = common_header_list):
    logging.debug('assert_headers %s', str(header_list) )
    for h in header_list:
        assert(r1['header'][h]  == r2['header'][h] )

def random_name():
    return str(random.randint(1024*1024,1024*1024*1024))

object_name_cases = [
'/a', 
'/a b',
]
local_file_cases = [
    'test/data/1024B.data', 
    'test/data/1025B.data',
]

if ENABLE_LARGE:
    object_name_cases += [
'/ xxx ',
'/ xxx /abc ',
'/你 好',
    ]

    local_file_cases += [
'test/data/1M+1.data', 
    ]



class TestPybcs(unittest.TestCase):
    def _test_bucket(self, bcs):
        lst = bcs.list_buckets() #LIST bucket，列出属于自己的bucket
        for b in lst:
            print b
            
    def __test_obj_put_file(self, bucket, object_name, local_file):
        local_file_content = open(local_file, 'rb').read()
        print '__test_obj_put_file(%s, %s)' % (object_name, local_file)
        o1 = bucket.object(object_name)

        o1.put_file(local_file)
        r1 = o1.get_to_file('test/data/tmp1.data')
        assert(pybcs.common.md5_for_file(local_file) == pybcs.common.md5_for_file('test/data/tmp1.data'))
        
        o1.post_file(local_file)
        r1 = o1.get_to_file('test/data/tmp1.data')
        assert(pybcs.common.md5_for_file(local_file) == pybcs.common.md5_for_file('test/data/tmp1.data'))

        o1.put(local_file_content)
        r1 = o1.get_to_file('test/data/tmp1.data')
        assert(pybcs.common.md5_for_file(local_file) == pybcs.common.md5_for_file('test/data/tmp1.data'))

        r2 = o1.get()
        assert(local_file_content == r2['body'])


    def _test_obj(self, bucket):
        for object_name in object_name_cases:
            for local_file in local_file_cases:
                self.__test_obj_put_file(bucket, object_name, local_file)

    def _test_acl(self, bucket):
        o1 = bucket.object('/obj'+str(int(time.time())))
		o1.put_fle('test/data/tmp1.data')
        r1 = o1.get()
        #assert the public can't download
        self.assertRaises(pybcs.HTTPException, o1.c.get, o1.public_get_url)
        self.assertRaises(pybcs.HTTPException, o1.c.head, o1.public_get_url)

        
        o1.make_public()
        #assert public can download
        r2 = o1.c.get(o1.public_get_url)

        o1.make_private_to_user(USER)
        self.assertRaises(pybcs.HTTPException, o1.c.get, o1.public_get_url)
        self.assertRaises(pybcs.HTTPException, o1.c.head, o1.public_get_url)


    def _test_list_object(self, bucket): #TODO
        def list_all(prefix):
            start = 0
            while True:
                lst = bucket.list_objects(prefix, start=start, limit = 100)
                if len(lst) == 0: break
                start += len(lst)
                for obj in lst:
                    yield obj
        def exists_in_list(object_name):
            for o in list_all('/'):
                if o.object_name == object_name: return True
            return False


        tmp_name = '/obj-' + random_name() 
        assert(exists_in_list(tmp_name) == False)

        o1 = bucket.object(tmp_name)
        o1.put_file('test/data/1024B.data')
        assert(exists_in_list(tmp_name) == True)


    def _test_object_copy(self, bucket): #TODO
        o1 = bucket.object('/obj')
        o2 = bucket.object('/dst')

        o1.put_file('test/data/1024B.data')
        o1.copy_to(o2, {'content-type': ''})

        r1 = o1.get_to_file('test/data/tmp1.data')
        r2 = o2.get_to_file('test/data/tmp2.data')

        assert(pybcs.common.md5_for_file('test/data/tmp1.data') == 
               pybcs.common.md5_for_file('test/data/tmp2.data'))
        assert_headers(r1, r2)
        
        o2.setmeta({'content-type': 'xxxxx'})
        r2 = o2.get_to_file('test/data/tmp2.data')
        assert(r2['header']['content-type'] == 'xxxxx')
        assert_headers(r1, r2, common_header_list - set(['content-type']))


        o2.setmeta({'x-bs-meta-abc': 'this is the value of meta-abc'})
        r2 = o2.get_to_file('test/data/tmp2.data')
        assert(r2['header']['x-bs-meta-abc'] == 'this is the value of meta-abc')
        assert_headers(r1, r2, common_header_list - set(['content-type']))

    def _test_superfile(self, bucket):#TODO

        o1 = bucket.object('/sub_o1')
        o2 = bucket.object('/sub_o2')

        o1.put_file('test/data/1.data')
        o2.put_file('test/data/100K.data')

        sup = bucket.superfile('/sup', [o1, o2])
        sup.put()

        sup.get_to_file('test/data/tmp1.data')

        assert(open('test/data/1.data', 'rb').read() + open('test/data/100K.data', 'rb').read() == 
                open('test/data/tmp1.data', 'rb').read()
              )

    def _test_superfile2(self, bucket):#TODO
        o1 = bucket.object('/sub_o1')
        o1.put_file('test/data/1.data')

        # 1000 sub objs
        sup = bucket.superfile('/sup', [o1] * 1024)
        sup.put()

        sup.get_to_file('test/data/tmp1.data')

        assert(open('test/data/1.data', 'rb').read() * 1024 == 
                open('test/data/tmp1.data', 'rb').read()
              )

        # too many sub objs
        sup = bucket.superfile('/sup', [o1] * 1025)

        self.assertRaises(pybcs.HTTPException, sup.put)


    def _run_test(self, bcs, bucket_name):
        bucket = bcs.bucket(bucket_name)

        self._test_bucket(bcs)
        self._test_list_object(bucket)

        self._test_obj(bucket)
        self._test_acl(bucket)
        self._test_object_copy(bucket)
        self._test_superfile(bucket)
        self._test_superfile2(bucket)

    def test_1(self):
        print 'test with pybcs.PyCurlHTTPC'
        bcs = pybcs.BCS(HOST, AK, SK, pybcs.PyCurlHTTPC)
        self._run_test(bcs, BUCKET)

    def test_2(self):
        print 'test with pybcs.HttplibHTTPC'
        bcs = pybcs.BCS(HOST, AK, SK, pybcs.HttplibHTTPC)
        self._run_test(bcs, BUCKET)

if __name__ == '__main__':
    unittest.main()

