# -*- coding: utf-8 -*-
"""
"""
import hashlib

from shake import to_unicode
from shake_auth.utils import *


def test_pbkdf2():
    def check(data, salt, iterations, keylen, expected):
        rv = pbkdf2(data, salt, iterations, keylen, hashfunc=hashlib.sha1)
        assert rv == expected

    # From RFC 6070
    check('password', 'salt', 1, 20,
          '0c60c80f961f0e71f3a9b524af6012062fe037a6')
    check('password', 'salt', 2, 20,
          'ea6c014dc72d6f8ccd1ed92ace1d41f0d8de8957')
    check('password', 'salt', 4096, 20,
          '4b007901b765489abead49d926f721d065a429c1')
    check('passwordPASSWORDpassword', 'saltSALTsaltSALTsaltSALTsaltSALTsalt',
          4096, 25, '3d2eec4fe41c849b80c8d83662c0e44a8b291a964cf2f07038')
    check('pass\x00word', 'sa\x00lt', 4096, 16,
          '56fa6aa75548099dcc37d7f03425e0c3')

    # From Crypt-PBKDF2
    check('password', 'ATHENA.MIT.EDUraeburn', 1, 16,
          'cdedb5281bb2f801565a1122b2563515')
    check('password', 'ATHENA.MIT.EDUraeburn', 1, 32,
          'cdedb5281bb2f801565a1122b25635150ad1f7a04bb9f3a333ecc0e2e1f70837')
    check('password', 'ATHENA.MIT.EDUraeburn', 2, 16,
          '01dbee7f4a9e243e988b62c73cda935d')
    check('password', 'ATHENA.MIT.EDUraeburn', 2, 32,
          '01dbee7f4a9e243e988b62c73cda935da05378b93244ec8f48a99e61ad799d86')
    check('password', 'ATHENA.MIT.EDUraeburn', 1200, 32,
          '5c08eb61fdf71e4e4ec3cf6ba1f5512ba7e52ddbc5e5142f708a31e2e62b1e13')
    check('X' * 64, 'pass phrase equals block size', 1200, 32,
          '139c30c0966bc32ba55fdbf212530ac9c5ec59f1a452f5cc9ad940fea0598ed1')
    check('X' * 65, 'pass phrase exceeds block size', 1200, 32,
          '9ccad6d468770cd51b10e6a68721be611a8b4d282601db3b36be9246915ec82a')


def test_hash_sha256():
    def check(data, salt, cost, expected):
        rv = hash_sha256(data, salt, cost)
        assert rv == expected

    check('password', 'salt', 10,
        'dsha256$10$salt$231afb7dcd2e860cfd58ab13372bd12c923076c3598a1219')
    check('password', 'salt', 8,
        'dsha256$8$salt$951ad61af6eb7d8126db061d25488e844625313aee9ec511')
    check('passwordPASSWORDpassword', 'saltSALTsaltSALTsaltSALTsaltSALTsalt',
          12, 'dsha256$12$saltSALTsaltSALTsaltSALTsaltSALTsalt$348c89dbcbd32b2f32d814b8116e84cf2b17347ebc180018')


def test_hash_sha512():
    def check(data, salt, cost, expected):
        rv = hash_sha512(data, salt, cost)
        assert rv == expected

    check('password', 'salt', 10,
        'dsha512$10$salt$f2104afdc09b36cab1de2d82c45d8f047d624eeab365410c')
    check('password', 'salt', 8,
        'dsha512$8$salt$9684295ee0d2b8e70611d09aaf9a519e9bd608b4b7e2a79d')
    check('passwordPASSWORDpassword', 'saltSALTsaltSALTsaltSALTsaltSALTsalt',
          12, 'dsha512$12$saltSALTsaltSALTsaltSALTsaltSALTsalt$8c0511f4c6e597c6ac6315d8f0362e225f3c501495ba23b8')


def test_hash_bcrypt():
    def check(data, salt, cost, expected):
        rv = hash_bcrypt(data, salt, cost=cost)
        assert rv == expected

    check('password', '$2a$10$HJYi2/Euv30.8OImamGFee', 10,
        'bcrypt$10$HJYi2/Euv30.8OImamGFeeFfdwv0axe0t.xppRVh3xawL.785hMDC')
    check('password', '$2a$08$iw9dkSkyAus2c3BLYwM1hO', 8,
        'bcrypt$08$iw9dkSkyAus2c3BLYwM1hOrjEsCsGjjP1X2LJFilJay9Pjl3WH96.')
    check('passwordPASSWORDpassword', '$2a$12$s6IoFdLT6cz0E4SswG.wle', 12,
        'bcrypt$12$s6IoFdLT6cz0E4SswG.wlelI1cwygywZGpKVJi4l6K8Db8./GFpKe')
    check('X'*65, '$2a$04$T4DjAITD1jGjrpb2hjiaRu', 4,
        'bcrypt$04$T4DjAITD1jGjrpb2hjiaRu5OuGBdWI/rF/YiO88MXEvkQq6DLMIlm')


def test_hash_scrypt():
    def check(data, salt, cost, expected):
        rv = hash_scrypt(data, salt, cost=cost)
        print to_unicode(rv)
        # assert rv == expected

    check('password', 'salt', 10,
        'scrypt$10$salt$16dbc8906763c7f048977a68f9d305f7710e068ca2cd95dab372125bb3f19608175003c79f9cdee65d2e45fc1f169afde0a6806f5d4f2ba0584249d2e66c2c96')
    check('password', 'salt', 8,
        'scrypt$8$salt$3cf2ff249f6592a84fc509f6799edfbd9e4b618c102edd5da6bbd0ca5b79cbb22f3bbeda40029b4738d70244be5113b764e73f2deb83c485332db2e9c3c16949')
    check('passwordPASSWORDpassword', 'saltSALTsaltSALTsaltSALTsaltSALTsalt', 12,
        'scrypt$12$saltSALTsaltSALTsaltSALTsaltSALTsalt$cc809d233840966826707fffdbe06712c784358de2b43788f7d8add0f6990a8901d3164ce36ed641f81cd5890cbb4c43a3a5209131a54a032741326ff3bceab2')
    check('X'*65, 'salt', 4,
        'scrypt$4$salt$ed7e36ecc4ca9ef8c78d99d51e89c02142712e5e43cd93201fe907413eb89575d4eea099958d65fba2ec30639ede4ceff4c904587a824a891e2a6310c09b5edf')

