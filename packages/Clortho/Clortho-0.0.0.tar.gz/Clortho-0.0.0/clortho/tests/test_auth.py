#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
#
#
# Copyright 2012 ShopWiki
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from unittest import TestCase
import bcrypt

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from clortho.auth import UserBase

class TestUser(UserBase):
    __tablename__ = 'test_users'

def get_engine():
    return create_engine('sqlite:///:memory:')

def get_session_cls():
    return sessionmaker(bind=get_engine())

class UserBaseTestCase(TestCase):
    def setUp(self):
        self.engine = get_engine()
        TestUser.metadata.create_all(self.engine)
        self.sql_session = sessionmaker(bind=self.engine)()

    def test_user_init(self):
        """
        Creating user and then testing the object's attributes.
        """
        user1 = TestUser(email=u'example@example.com')
        
        self.assertEqual(user1.email, 'example@example.com')
        self.assertFalse(user1.password_is_set)
        self.assertFalse(user1.disabled)
        self.assertFalse(user1.activated)

    def test_user_repr(self):
        """
        Testing printed output of user.
        """
        user1 = TestUser(email=u'example@example.com')
        self.assertEqual(str(user1), '<User(\'example@example.com\')>')
        
    def test_adding_to_db(self):
        """
        Creating user and adding to a database, then making sure user is in 
        db (and that this is the only user in the database with the unique 
        email address).
        """
        user1 = TestUser(email=u'example@example.com')
        self.sql_session.add(user1)
        self.sql_session.commit()

        # make sure there is only one record with this email address
        user1 = self.sql_session.query(TestUser)\
                                .filter_by(email=u'example@example.com')\
                                .one()
        self.assertEqual(user1.email, 'example@example.com')

    def test_duplicate_emails(self):
        """
        Try creating two users with the same email address.
        """
        user1 = TestUser(email=u'example@example.com')
        self.sql_session.add(user1)
        self.sql_session.commit()

        with self.assertRaises(IntegrityError):
            user2 = TestUser(email=u'example@example.com')
            self.sql_session.add(user2)
            self.sql_session.commit()

    def test_password(self):
        """
        Testing setting the user's password and then checking the updated 
        object.
        """
        user1 = TestUser(email=u'example@example.com')
        user1.set_password('pwd')

        self.assertTrue(user1.check_password('pwd'))
        self.assertFalse(user1.check_password('pwdd'))
        self.assertTrue(user1.password_is_set)
        self.assertEqual(user1.password_hash,
                         bcrypt.hashpw('pwd', user1.password_hash))

    def test_activation_code(self):
        """
        Generating an activation code and testing updated user object.
        """
        user1 = TestUser(email=u'example@example.com')
        activation_code = user1.generate_activation_code()

        # activation_code is not None
        self.assertTrue(activation_code)

        self.assertEqual(user1.activation_code_hash, 
                         bcrypt.hashpw(activation_code, 
                                       user1.activation_code_hash))

    def test_activate(self):
        """
        Activating a user from an activation code. Making sure they cannot 
        be "activated" again using the same code.
        """
        user1 = TestUser(email=u'example@example.com')
        original_activation_code = user1.generate_activation_code()
        # print original_activation_code

        # still not yet activated
        self.assertFalse(user1.activated)

        user1.activate(original_activation_code)

        # now activated, but activation code changed (user should not be 
        # able to use activation code again)
        self.assertTrue(user1.activated)
        
        with self.assertRaises(Exception):
            user1.activate(original_activation_code)

    def test_user_fields(self):
        """
        Saving an activated user to the database, then pulling user from the 
        database and checking all attributes were set properly in the db.
        """
        user1 = TestUser(email=u'example@example.com')
        user1.set_password('pwd')
        activation_code = user1.generate_activation_code()
        user1.activate(activation_code)

        self.sql_session.add(user1)
        self.sql_session.commit()

        # make sure there is only one record with this email address
        user2 = self.sql_session.query(TestUser)\
                                .filter_by(email=u'example@example.com')\
                                .one()
        self.assertEqual(user2.email, 'example@example.com')

        # all fields should be set
        self.assertTrue(user2.id)
        self.assertTrue(user2.email)
        self.assertTrue(user2.password_hash)
        self.assertTrue(user2.password_is_set)
        self.assertFalse(user2.disabled)
        self.assertTrue(user2.activated)
        self.assertTrue(user2.activation_code_hash)
