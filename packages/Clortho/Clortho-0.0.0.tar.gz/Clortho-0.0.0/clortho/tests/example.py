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

import bcrypt

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from clortho.auth import UserBase, ActivationError

class SimpleUser(UserBase):
    __tablename__ = 'simple_users'

if __name__ == '__main__':
    engine = create_engine('sqlite:///:memory:')
    session = sessionmaker(bind=engine)()

    SimpleUser.metadata.create_all(engine)

    user1 = SimpleUser(email=u'example@example.com')
    session.add(user1)
    session.commit()

    # Users are unique by email
    try:
        user2 = SimpleUser(email=u'example@example.com')
        session.add(user2)
        session.commit()
    except IntegrityError:
        print "Users are unique by email!"
        session.rollback()

    user1.set_password('pwd')

    assert user1.check_password('pwd')
    assert user1.check_password('pwdd') == False
    assert user1.password_is_set
    assert user1.password_hash == bcrypt.hashpw('pwd', user1.password_hash)


    activation_code = user1.generate_activation_code()
    assert user1.activated == False
    user1.activate(activation_code)
    assert user1.activated

    user1.activated = False
    try:
        user1.activate(activation_code)
    except ActivationError:
        print "Activation codes only work once!"

    new_activation_code = user1.generate_activation_code()
    user1.activate(new_activation_code)
    assert user1.activated

    assert user1.disabled == False
    user1.disabled = True
    assert user1.disabled

    # Password checks fail no matter what if the user is disabled
    assert user1.check_password('pwd') == False
