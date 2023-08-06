# Copyright 2011 Canonical Ltd.
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

from django.contrib.auth.models import User
from django.test import (
    TestCase as DjangoTestCase,
    TransactionTestCase as DjangoTransactionTestCase,
    )
from testtools import TestCase as TesttoolsTestCase

from django_factory.factory import Factory

__all__ = [
    'TestCase',
    'TransactionTestCase',
    ]


def create_user(factory, password=None, **attrs):
    if password is None:
        password = "test"
    # We have to use _generate_instance here as prepare_one() leads
    # to infinite recursion. The desire to have a model generator that
    # creates an instance and # then modifies it might be common, so
    # there should perhaps be a public interface that enables that.
    user, _, _ = factory._generate_instance(User, save=False, attrs=attrs,
                                            not_including=[])
    user.set_password(password)
    return user


model_generators = {User: create_user}


# N.B. The order of the superclasses matters here.
#  if Django is first then when running under 2.6
#  TesttoolsTestCase.__init__() won't be called,
#  causing all sorts of havoc.

class TestCase(TesttoolsTestCase, DjangoTestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.factory = Factory(test_case=self,
                               model_generators=model_generators)


class TransactionTestCase(TesttoolsTestCase, DjangoTransactionTestCase):

    def setUp(self):
        super(TransactionTestCase, self).setUp()
        self.factory = Factory(test_case=self,
                               model_generators=model_generators)
