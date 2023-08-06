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

import datetime
from decimal import Decimal
from unittest import TestResult

from django.contrib.auth.models import User
from django.core import exceptions
from django.core.files.base import ContentFile
from django.db.models import fields as django_fields
from django.test import TestCase as DjangoTestCase

from testtools import (
    ExtendedToOriginalDecorator,
    TestCase,
    )
from testtools.matchers import StartsWith

from django_factory import generators, testcase
from django_factory.factory import DummyTestCase, Factory
from django_project.factory_tests import models as test_models


class TestGenerators(TestCase):

    def setUp(self):
        super(TestGenerators, self).setUp()
        self.field = test_models.ModelWithCharField._meta.get_field(
                'char_field')
        self.factory = Factory()

    def test_generate_boolean(self):
        generated = generators.generate_boolean(self.field, self.factory)
        self.assertIs(False, generated)

    def test_generate_unicode_generates_unicode(self):
        generated = generators.generate_unicode(self.field, self.factory)
        self.assertIsInstance(generated, unicode)

    def test_generate_unicode_starts_with_field_name(self):
        generated = generators.generate_unicode(self.field, self.factory)
        self.assertThat(generated, StartsWith(self.field.name))

    def test_generate_unicode_respects_max_length(self):
        field = test_models.ModelWithMaxLengthCharField._meta.get_field(
                'char_field')
        generated = generators.generate_unicode(field, self.factory)
        self.assertEquals(field.max_length, len(generated))

    def test_generate_unicode_handles_None_max_length(self):
        field = test_models.ModelWithNoneMaxLengthTextField._meta.get_field(
                'text_field')
        generated = generators.generate_unicode(field, self.factory)
        self.assertIsInstance(generated, unicode)

    def test_generate_int_generates_int(self):
        generated = generators.generate_int(self.field, self.factory)
        self.assertIsInstance(generated, int)

    def test_generate_float_generates_float(self):
        generated = generators.generate_float(self.field, self.factory)
        self.assertIsInstance(generated, float)

    def test_generate_decimal_generates_decimal(self):
        generated = generators.generate_decimal(self.field, self.factory)
        self.assertIsInstance(generated, Decimal)

    def test_generate_date_generates_date(self):
        generated = generators.generate_date(self.field, self.factory)
        self.assertIsInstance(generated, datetime.date)

    def test_generate_datetime_generates_datetime(self):
        generated = generators.generate_datetime(self.field, self.factory)
        self.assertIsInstance(generated, datetime.datetime)

    def test_generate_time_generates_time(self):
        generated = generators.generate_time(self.field, self.factory)
        self.assertIsInstance(generated, datetime.time)

    def test_generate_url_generates_unicode(self):
        generated = generators.generate_url(self.field, self.factory)
        self.assertIsInstance(generated, unicode)

    def test_generate_url_starts_with_http(self):
        generated = generators.generate_url(self.field, self.factory)
        self.assertThat(generated, StartsWith("http://"))

    def test_generate_email_generates_unicode(self):
        generated = generators.generate_email(self.field, self.factory)
        self.assertIsInstance(generated, unicode)

    def test_generate_email_contains_at(self):
        generated = generators.generate_email(self.field, self.factory)
        self.assertIn('@', generated)

    def test_generate_comma_separated_integer(self):
        generated = generators.generate_comma_separated_integer(self.field,
                self.factory)
        self.assertIsInstance(generated, str)

    def test_generate_comma_separated_integer_generates_str_int(self):
        generated = generators.generate_comma_separated_integer(self.field,
                self.factory)
        # Check that we can call int on the result
        int(generated)

    def test_generate_ip_address(self):
        generated = generators.generate_ip_address(self.field, self.factory)
        self.assertIsInstance(generated, str)

    def test_generate_ip_address_value(self):
        generated = generators.generate_ip_address(self.field, self.factory)
        parts = generated.split(".")
        self.assertEqual(4, len(parts))
        map(int, parts)

    def test_generate_generic_ip_address(self):
        generated = generators.generate_generic_ip_address(self.field, self.factory)
        self.assertIsInstance(generated, str)

    def test_generate_generic_ip_address_value(self):
        generated = generators.generate_generic_ip_address(self.field, self.factory)
        parts = generated.split("::")
        self.assertEqual(2, len(parts))

    def test_generate_file_generates_content_file(self):
        generated = generators.generate_file(self.field, self.factory)
        self.assertIsInstance(generated, ContentFile)

    def test_generate_file_contents_start_with_field_name(self):
        generated = generators.generate_file(self.field, self.factory)
        self.assertThat(generated.read(), StartsWith(self.field.name))


class FactoryGenerateValueTests(DjangoTestCase, TestCase):

    def get_factory_with_known_generator(self, field, expected, value):
        """Get a factory replacing the generator for the particular field class.

        Checks first that the default generator is as expected, and then
        creates a Factory that replaces the default with a function
        that returns the given value.

        :param field: the Field class that is being tested
        :param expected: the expected default generator for that class
        :param value: the value that the factory should return when
                generating a value for the Field class.
        :return: a Factory instance that will return ``value`` when
                generating a value for an instance of ``field``.
        :raises AssertionError: if the default generator for ``field``
                is not equal to ``expected``.
        """
        self.assertEqual(expected, Factory.DEFAULT_FIELD_MAPPING[field])
        mapping = Factory.DEFAULT_FIELD_MAPPING.copy()
        def return_value(_field, _factory):
            return value
        mapping[field] = return_value
        return Factory(field_mapping=mapping)

    def get_field(self, model, name):
        """Get the Field instance of the particular name from the model.

        Given a model this method will return the Field instance that
        is assigned the the named attribute on the model.

        :param model: the Model instance to take the field from.
        :param name: the attribute on the model that the field should
                be taken from.
        :return: The ``Field`` subclass that is assigned to ``name`` on
                ``model``.
        """
        return model._meta.get_field(name, many_to_many=True)

    def assertGeneratesValidValueFor(self, field):
        """Check that the value created for ``field`` passes validation.

        This asks the factory to generate a value for ``field`` using the default
        generator, and then checks the the value passes ``fields`` validators.

        :param field: the Field instance to check the value generated for.
        :return: None
        :raises ValidationError: If the value produced for ``field`` doesn't
            pass validation.
        :raise SkipTest: if the version of django in use doesn't support
            validators.
        """
        if getattr(django_fields.CharField, 'default_validators', None) is None:
            self.skip("This version of django doesn't support validators")
        factory = Factory()
        value = factory.generate_value(field)
        field.run_validators(value)

    def test_boolean_field(self):
        expected_value = True
        factory = self.get_factory_with_known_generator(
                django_fields.BooleanField, generators.generate_boolean,
                expected_value)
        model = test_models.ModelWithBooleanField
        field = self.get_field(model, 'bool_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_boolean_field_generates_valid_value(self):
        model = test_models.ModelWithBooleanField
        field = self.get_field(model, 'bool_field')
        self.assertGeneratesValidValueFor(field)

    def test_null_boolean_field(self):
        expected_value = True
        factory = self.get_factory_with_known_generator(
                django_fields.NullBooleanField, generators.generate_boolean,
                expected_value)
        model = test_models.ModelWithNullBooleanField
        field = self.get_field(model, 'bool_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_null_boolean_field_generates_valid_value(self):
        model = test_models.ModelWithNullBooleanField
        field = self.get_field(model, 'bool_field')
        self.assertGeneratesValidValueFor(field)

    def test_int_field(self):
        expected_value = 11111
        factory = self.get_factory_with_known_generator(
                django_fields.IntegerField, generators.generate_int,
                expected_value)
        model = test_models.ModelWithIntegerField
        field = self.get_field(model, 'int_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_int_field_generates_valid_value(self):
        model = test_models.ModelWithIntegerField
        field = self.get_field(model, 'int_field')
        self.assertGeneratesValidValueFor(field)

    def test_big_int_field(self):
        if getattr(django_fields, 'BigIntegerField', None) is None:
            self.skip("This version of django doesn't have BigIntegerField")
        expected_value = 11111
        factory = self.get_factory_with_known_generator(
                django_fields.BigIntegerField, generators.generate_int,
                expected_value)
        model = test_models.ModelWithBigIntegerField
        field = self.get_field(model, 'big_int_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_big_int_field_generates_valid_value(self):
        if getattr(django_fields, 'BigIntegerField', None) is None:
            self.skip("This version of django doesn't have BigIntegerField")
        model = test_models.ModelWithBigIntegerField
        field = self.get_field(model, 'big_int_field')
        self.assertGeneratesValidValueFor(field)

    def test_small_int_field(self):
        expected_value = 11111
        factory = self.get_factory_with_known_generator(
                django_fields.SmallIntegerField, generators.generate_int,
                expected_value)
        model = test_models.ModelWithSmallIntegerField
        field = self.get_field(model, 'small_int_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_small_int_field_generates_valid_value(self):
        model = test_models.ModelWithSmallIntegerField
        field = self.get_field(model, 'small_int_field')
        self.assertGeneratesValidValueFor(field)

    def test_positive_int_field(self):
        expected_value = 11111
        factory = self.get_factory_with_known_generator(
                django_fields.PositiveIntegerField, generators.generate_int,
                expected_value)
        model = test_models.ModelWithPositiveIntegerField
        field = self.get_field(model, 'positive_int_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_positive_int_field_generates_valid_value(self):
        model = test_models.ModelWithPositiveIntegerField
        field = self.get_field(model, 'positive_int_field')
        self.assertGeneratesValidValueFor(field)

    def test_positive_small_int_field(self):
        expected_value = 11111
        factory = self.get_factory_with_known_generator(
                django_fields.PositiveSmallIntegerField,
                generators.generate_int, expected_value)
        model = test_models.ModelWithPositiveSmallIntegerField
        field = self.get_field(model, 'positive_small_int_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_positive_small_int_field_generates_valid_value(self):
        model = test_models.ModelWithPositiveSmallIntegerField
        field = self.get_field(model, 'positive_small_int_field')
        self.assertGeneratesValidValueFor(field)

    def test_float_field(self):
        expected_value = 111.11
        factory = self.get_factory_with_known_generator(
                django_fields.FloatField,
                generators.generate_float, expected_value)
        model = test_models.ModelWithFloatField
        field = self.get_field(model, 'float_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_float_field_generates_valid_value(self):
        model = test_models.ModelWithFloatField
        field = self.get_field(model, 'float_field')
        self.assertGeneratesValidValueFor(field)

    def test_decimal_field(self):
        expected_value = Decimal(1111)
        factory = self.get_factory_with_known_generator(
                django_fields.DecimalField,
                generators.generate_decimal, expected_value)
        model = test_models.ModelWithDecimalField
        field = self.get_field(model, 'decimal_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_decimal_field_generates_valid_value(self):
        model = test_models.ModelWithDecimalField
        field = self.get_field(model, 'decimal_field')
        self.assertGeneratesValidValueFor(field)

    def test_char_field(self):
        expected_value = "aaaaaa"
        factory = self.get_factory_with_known_generator(
                django_fields.CharField,
                generators.generate_unicode, expected_value)
        model = test_models.ModelWithCharField
        field = self.get_field(model, 'char_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_char_field_generates_valid_value(self):
        model = test_models.ModelWithCharField
        field = self.get_field(model, 'char_field')
        self.assertGeneratesValidValueFor(field)

    def test_text_field(self):
        expected_value = "aaaaaa"
        factory = self.get_factory_with_known_generator(
                django_fields.TextField,
                generators.generate_unicode, expected_value)
        model = test_models.ModelWithTextField
        field = self.get_field(model, 'text_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_text_field_generates_valid_value(self):
        model = test_models.ModelWithTextField
        field = self.get_field(model, 'text_field')
        self.assertGeneratesValidValueFor(field)

    def test_slug_field(self):
        expected_value = "aaaaaa"
        factory = self.get_factory_with_known_generator(
                django_fields.SlugField,
                generators.generate_unicode, expected_value)
        model = test_models.ModelWithSlugField
        field = self.get_field(model, 'slug_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_slug_field_generates_valid_value(self):
        model = test_models.ModelWithSlugField
        field = self.get_field(model, 'slug_field')
        self.assertGeneratesValidValueFor(field)

    def test_date_field(self):
        expected_value = datetime.date(2010, 10, 10)
        factory = self.get_factory_with_known_generator(
                django_fields.DateField,
                generators.generate_date, expected_value)
        model = test_models.ModelWithDateField
        field = self.get_field(model, 'date_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_date_field_generates_valid_value(self):
        model = test_models.ModelWithDateField
        field = self.get_field(model, 'date_field')
        self.assertGeneratesValidValueFor(field)

    def test_datetime_field(self):
        expected_value = datetime.datetime(2010, 10, 10)
        factory = self.get_factory_with_known_generator(
                django_fields.DateTimeField,
                generators.generate_datetime, expected_value)
        model = test_models.ModelWithDateTimeField
        field = self.get_field(model, 'datetime_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_datetime_field_generates_valid_value(self):
        model = test_models.ModelWithDateTimeField
        field = self.get_field(model, 'datetime_field')
        self.assertGeneratesValidValueFor(field)

    def test_time_field(self):
        expected_value = datetime.time(10, 10)
        factory = self.get_factory_with_known_generator(
                django_fields.TimeField,
                generators.generate_time, expected_value)
        model = test_models.ModelWithTimeField
        field = self.get_field(model, 'time_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_time_field_generates_valid_value(self):
        model = test_models.ModelWithTimeField
        field = self.get_field(model, 'time_field')
        self.assertGeneratesValidValueFor(field)

    def test_url_field_default_generator(self):
        expected_value = "http://example.com/aaaaaa"
        factory = self.get_factory_with_known_generator(
                django_fields.URLField,
                generators.generate_url, expected_value)
        model = test_models.ModelWithURLField
        field = self.get_field(model, 'url_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_url_field_generates_valid_value(self):
        model = test_models.ModelWithURLField
        field = self.get_field(model, 'url_field')
        self.assertGeneratesValidValueFor(field)

    def test_email_field(self):
        expected_value = "aaaaa@example.com"
        factory = self.get_factory_with_known_generator(
                django_fields.EmailField,
                generators.generate_email, expected_value)
        model = test_models.ModelWithEmailField
        field = self.get_field(model, 'email_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_email_field_generates_valid_value(self):
        model = test_models.ModelWithEmailField
        field = self.get_field(model, 'email_field')
        self.assertGeneratesValidValueFor(field)

    def test_comma_separated_integer_field(self):
        expected_value = "1,2,3"
        factory = self.get_factory_with_known_generator(
                django_fields.CommaSeparatedIntegerField,
                generators.generate_comma_separated_integer,
                expected_value)
        model = test_models.ModelWithCommaSeparatedIntegerField
        field = self.get_field(model, 'csi_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_comma_separated_integer_field_generates_valid_value(self):
        model = test_models.ModelWithCommaSeparatedIntegerField
        field = self.get_field(model, 'csi_field')
        self.assertGeneratesValidValueFor(field)

    def test_ip_address_field(self):
        expected_value = "192.111.10.1"
        factory = self.get_factory_with_known_generator(
                django_fields.IPAddressField,
                generators.generate_ip_address,
                expected_value)
        model = test_models.ModelWithIPAddressField
        field = self.get_field(model, 'ip_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_ip_address_field_generates_valid_value(self):
        model = test_models.ModelWithIPAddressField
        field = self.get_field(model, 'ip_field')
        self.assertGeneratesValidValueFor(field)

    def test_generic_ip_address_field(self):
        if getattr(django_fields, 'GenericIPAddressField', None) is None:
            self.skip("This version of django has no GenericIPAddressField")
        expected_value = "192.111.10.1"
        factory = self.get_factory_with_known_generator(
                django_fields.GenericIPAddressField,
                generators.generate_generic_ip_address,
                expected_value)
        model = test_models.ModelWithGenericIPAddressField
        field = self.get_field(model, 'ip_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_generic_ip_address_field_generates_valid_value(self):
        if getattr(django_fields, 'GenericIPAddressField', None) is None:
            self.skip("This version of django has no GenericIPAddressField")
        model = test_models.ModelWithGenericIPAddressField
        field = self.get_field(model, 'ip_field')
        self.assertGeneratesValidValueFor(field)

    def test_file_field(self):
        expected_value = ContentFile("aaa")
        factory = self.get_factory_with_known_generator(
                django_fields.files.FileField,
                generators.generate_file,
                expected_value)
        model = test_models.ModelWithFileField
        field = self.get_field(model, 'file_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_file_field_generates_valid_value(self):
        model = test_models.ModelWithFileField
        field = self.get_field(model, 'file_field')
        self.assertGeneratesValidValueFor(field)

    def test_image_field(self):
        expected_value = ContentFile("aa")
        factory = self.get_factory_with_known_generator(
                django_fields.files.ImageField,
                generators.generate_file,
                expected_value)
        model = test_models.ModelWithImageField
        field = self.get_field(model, 'image_field')
        value = factory.generate_value(field)
        self.assertEqual(expected_value, value)

    def test_image_field_generates_valid_value(self):
        model = test_models.ModelWithImageField
        field = self.get_field(model, 'image_field')
        self.assertGeneratesValidValueFor(field)

    def test_chooses_from_choices(self):
        # When a field has choices, those choices are used when
        # generating a value for that field.
        factory = Factory()
        model = test_models.ModelWithChoices
        field = self.get_field(model, 'choices_field')
        value = factory.generate_value(field)
        self.assertEqual(test_models.ModelWithChoices.CHOICES[0][0],
                value)

    def test_chooses_from_choices_with_groups(self):
        # Still selects the first choice, even if there are choice
        # groups.
        factory = Factory()
        model = test_models.ModelWithChoiceGroups
        field = self.get_field(model, 'choices_field')
        value = factory.generate_value(field)
        self.assertEqual(test_models.ModelWithChoiceGroups.CHOICES[0][1][0][0],
                value)

    def test_type_error_on_unknown_field(self):
        factory = Factory()
        class Field(django_fields.Field):
            pass
        field = Field()
        self.assertRaises(TypeError, factory.generate_value, field)


class TestFactory(TestCase, DjangoTestCase):

    def test_get_fields_with_no_fields(self):
        fields = Factory.get_fields(test_models.ModelWithNoFields)
        self.assertEqual([], fields)

    def test_get_fields_returns_normal_fields(self):
        fields = Factory.get_fields(test_models.ModelWithCharField)
        self.assertEqual([test_models.ModelWithCharField._meta.get_field_by_name('char_field')[0]], fields)

    def test_get_fields_returns_many_to_many_field(self):
        fields = Factory.get_fields(test_models.ModelWithSelfManyToManyField)
        self.assertEqual([test_models.ModelWithSelfManyToManyField._meta.get_field_by_name('things')[0]], fields)

    def test_make_one_makes_one(self):
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithNoFields)
        self.assertIsInstance(instance, test_models.ModelWithNoFields)

    def test_make_one_saves(self):
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithNoFields)
        # Raises DoesNotExist if it wasn't saved
        test_models.ModelWithNoFields.objects.filter(pk=instance.pk).get()

    def test_prepare_one_makes_one(self):
        factory = Factory()
        instance = factory.prepare_one(test_models.ModelWithNoFields)
        self.assertIsInstance(instance, test_models.ModelWithNoFields)

    def test_prepare_one_doesnt_save(self):
        factory = Factory()
        instance = factory.prepare_one(test_models.ModelWithNoFields)
        self.assertRaises(test_models.ModelWithNoFields.DoesNotExist,
            test_models.ModelWithNoFields.objects.filter(pk=instance.pk).get)

    def test_make_one_generates_value(self):
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithCharField)
        self.assertIsInstance(instance.char_field, unicode)
        self.assert_("NOT_PROVIDED" not in instance.char_field)

    def test_make_one_uses_passed_value(self):
        factory = Factory()
        value = u'bar'
        instance = factory.make_one(test_models.ModelWithCharField, char_field=value)
        self.assertEquals(value, instance.char_field)

    def test_make_one_doesnt_generate_for_null_and_blank(self):
        # When a field has null=True and blank=True, no value is generated
        # for it by default.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithNullAndBlankCharField)
        self.assertEquals(None, instance.char_field)

    def test_make_one_doesnt_generate_for_null_only(self):
        # When a field has null=True and not blank=True, a value is generated
        # for it by default.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithNullCharField)
        self.assertIsInstance(instance.char_field, unicode)

    def test_make_one_doesnt_generate_for_blank_only(self):
        # When a field has blank=True and not null=True, a value is generated
        # for it by default.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithBlankCharField)
        self.assertIsInstance(instance.char_field, unicode)

    def test_make_one_doesnt_generates_for_null_if_factory_method(self):
        # If there is a factory method on the model for a field, that is
        # used even if the field has null=True and blank=True
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithNullAndBlankCharFieldAndFactory)
        self.assertEquals(test_models.ModelWithNullAndBlankCharFieldAndFactory.VALUE,
                instance.char_field)

    def test_make_one_uses_default(self):
        # When a field has a default set, that is used when generating a
        # value for that field.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithDefaultCharField)
        self.assertEquals(test_models.ModelWithDefaultCharField.DEFAULT,
                instance.char_field)

    def test_make_one_uses_callable_default(self):
        # If a field has a callable default, that is correctly handled
        # by using the return value of the callable.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithCallableDefaultCharField)
        self.assertEquals(test_models.ModelWithCallableDefaultCharField.DEFAULT,
                instance.char_field)

    def test_make_one_doesnt_use_default_if_factory_method(self):
        # If there is a factory generator method for a field, that is
        # used in preference to any default.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithDefaultCharFieldAndFactory)
        self.assertEquals(test_models.ModelWithDefaultCharFieldAndFactory.VALUE,
                instance.char_field)

    def test_make_one_uses_field_factory(self):
        # Any factory generator method for a field is used to get the
        # value for that field.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithFieldGenerator)
        self.assertEquals(test_models.ModelWithFieldGenerator.VALUE,
                instance.char_field)

    def test_make_one_uses_passed_value_over_factory(self):
        # Any value passed to make_one will be used in preference to any
        # generator for that field.
        factory = Factory()
        value = 'aaaa'
        instance = factory.make_one(test_models.ModelWithFieldGenerator,
                char_field=value)
        self.assertEquals(value, instance.char_field)

    def test_make_one_uses_generator_for_instance(self):
        # If a model has a factory instance generator that is used when
        # make_one is called for that model.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithInstanceGenerator)
        self.assertEqual(test_models.ModelWithFieldGenerator.VALUE,
                instance.char_field)

    def test_make_one_validates_model(self):
        # Any validators on the model are checked before the model is
        # returned in order to save surprises.
        # validators are new in django 1.2, so skip the test on earlier
        # releases
        if getattr(django_fields.CharField, 'default_validators', None) is None:
            self.skip("This version of django doesn't support validators")
        factory = Factory()
        self.assertRaises(exceptions.ValidationError,
                factory.make_one, test_models.ModelWithImpossibleValidator)

    def test_prepare_one_doesnt_validate_model(self):
        # When calling prepare_one the validators aren't run, as
        # foreignkey constraints can't be properly satisfied if
        # the model isn't being saved
        if getattr(django_fields.CharField, 'default_validators', None) is None:
            self.skip("This version of django doesn't support validators")
        factory = Factory()
        instance = factory.prepare_one(test_models.ModelWithImpossibleValidator)
        self.assertIsInstance(instance,
                test_models.ModelWithImpossibleValidator)

    def test_make_one_makes_one_of_many_to_many_target(self):
        # If there is a ManyToManyField on the model, one instance of
        # the target is generated.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithManyToManyField)
        self.assertEqual(1, instance.things.count())
        self.assertIsInstance(instance.things.get(),
                test_models.ModelReferencedByManyToManyField)

    def test_make_one_uses_generator_for_many_to_many(self):
        # If the model has a factory generator function for the many to
        # many field then it is used when creating the instance of the
        # ManyToManyField target.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithManyToManyFieldAndFactory)
        self.assertEqual(1, instance.things.count())
        self.assertEqual(test_models.ModelWithManyToManyFieldAndFactory.VALUE,
                instance.things.get())

    def test_make_one_makes_specified_number_of_many_to_many_target(self):
        # If there is a factory attribute specifying the number of
        # instances of a ManyToManyField target to make, then that is
        # obeyed when construcing the instances.
        factory = Factory()
        instance = factory.make_one(
                test_models.ModelWantingTwoManyToManyInstances)
        self.assertEqual(2, instance.things.count())

    def test_make_one_uses_callable_number_of_many_to_many_instances(self):
        # If the factory attribute specifying the number of instances of
        # a ManyToManyField is a callable, then it is called and the
        # resulting number of instances are created.
        factory = Factory()
        instance = factory.make_one(
                test_models.ModelWithCallableSpecifiedManyToManyField)
        self.assertEqual(test_models.ModelWithCallableSpecifiedManyToManyField.COUNT,
                instance.things.count())

    def test_make_one_makes_zero_instances_of_many_to_many_target_if_desired(self):
        # If the model factory specifies zero instances of a
        # ManyToManyField should be created, then don't create any.
        factory = Factory()
        instance = factory.make_one(
                test_models.ModelWantingZeroManyToManyInstances)
        self.assertEqual(0, instance.things.count())

    def test_make_one_uses_value_for_many_to_many_target(self):
        # If a value is passed to make_one for a ManyToManyField then it
        # is used rather than creating any instances.
        factory = Factory()
        target = factory.make_one(test_models.ModelReferencedByManyToManyField)
        instance = factory.make_one(test_models.ModelWithManyToManyFieldAndFactory,
                things=[target])
        self.assertEqual(1, instance.things.count())
        self.assertEqual(target.pk, instance.things.get().pk)

    def test_make_one_with_empty_list_passed(self):
        # If an empty list is passed to make_one for a ManyToManyField then
        # no values are generated
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithManyToManyField,
                things=[])
        self.assertEqual(0, instance.things.count())

    def test_make_one_makes_none_of_many_to_many_target_when_null(self):
        # When null=True is set on a ManyToManyField create no instances
        # of the target model
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithNullManyToManyField)
        self.assertEqual(0, instance.things.count())

    def test_make_one_uses_many_to_many_generator_when_null(self):
        # If there is a factory generator function for a ManyToMany
        # field then it is used even when null=True is set on that
        # field.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithNullManyToManyFieldAndFactory)
        self.assertEqual(1, instance.things.count())
        self.assertEqual(test_models.ModelWithNullManyToManyFieldAndFactory.VALUE,
                instance.things.get())

    def test_make_one_breaks_many_to_many_reference_loop(self):
        # Any loops between models with ManyToManyField are broken.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithCircularReferenceLoop1)
        self.assertEqual(1, instance.things.count())
        self.assertEqual(0, instance.things.get().other_things.count())

    def test_make_one_breaks_many_to_many_self_reference_loop(self):
        # If a model referenes itself in a ManyToManyField the loop will
        # be broken after creating one target instance for the first
        # instance created.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithSelfManyToManyField)
        self.assertEqual(1, instance.things.count())
        self.assertEqual(0, instance.things.get().things.count())

    def test_make_one_creates_needed_instances_of_through_models(self):
        # When a ManyToManyField has a through model, instances of that
        # through model are created as needed.
        factory = Factory()
        instance = factory.make_one(test_models.Group)
        self.assertEqual(1, instance.people.count())
        person = instance.people.get()
        self.assertIsInstance(person, test_models.Person)
        self.assertEqual(instance, person.group_set.get())
        membership = person.membership_set.get()
        self.assertIsInstance(membership, test_models.Membership)
        self.assertIsInstance(membership.comment, unicode)

    def test_make_one_makes_one_of_foreign_key_target(self):
        # An instance is created for any ForeignKey on the model.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithForeignKey)
        self.assertIsInstance(instance.thing,
                test_models.ModelReferencedByForiegnKeyField)

    def test_make_one_doesnt_make_one_of_foreign_key_if_null_and_blank(self):
        # If null=True and blank=True on a ForeignKey then no instance
        # will be generated.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithNullAndBlankForeignKey)
        self.assertEqual(None, instance.thing)

    def test_make_one_makes_one_of_foreign_key_target_if_just_null(self):
        # If just null=True but not blank=True on a ForeignKey then a
        # reference will be generated.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithNullForeignKey)
        self.assertIsInstance(instance.thing,
                test_models.ModelReferencedByForiegnKeyField)

    def test_make_one_makes_one_of_foreign_key_target_if_just_blank(self):
        # If just blank=True but not null=True on a ForeignKey then a
        # reference will be generated.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithBlankForeignKey)
        self.assertIsInstance(instance.thing,
                test_models.ModelReferencedByForiegnKeyField)

    def test_make_one_uses_factory_for_foreign_key(self):
        # If there is a factory generator function for a ForeignKey
        # field then it will be used.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithForeignKeyAndFactory)
        self.assertEqual(test_models.ModelWithForeignKeyAndFactory.VALUE, instance.thing)

    def test_make_one_uses_passed_value_for_foreign_key(self):
        # If you pass a value for a ForeignKey then it will be used
        # rather than any factory generator function.
        factory = Factory()
        value = test_models.ModelReferencedByForiegnKeyField()
        instance = factory.make_one(test_models.ModelWithForeignKeyAndFactory,
                thing=value)
        self.assertEqual(value, instance.thing)

    def test_make_one_uses_None_as_passed_value_for_foreign_key(self):
        # If you pass a None value for a ForeignKey then it will be used
        # rather than any factory generator function.
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithNullAndBlankForeignKey,
                thing=None)
        self.assertEqual(None, instance.thing)

    def test_make_one_breaks_foreign_key_reference_loop(self):
        # If there is a loop between models using ForeignKey references,
        # then it will be broken on the model that has null=True and
        # blank=True
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithCircularForiegnKeyReferenceLoop1)
        self.assertIsInstance(instance.thing, test_models.ModelWithCircularForiegnKeyReferenceLoop2)
        self.assertEqual(None, instance.thing.thing)

    def test_make_one_saves_foreign_key_foreign_key(self):
        # When creating an instance needed for foreign keys, it saves
        # the instance, and so can satisfy any foreign key constraints
        # on the foreign key model
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithForiegnKeyToModelWithForeignKey)
        self.assertIsInstance(instance,
                test_models.ModelWithForiegnKeyToModelWithForeignKey)
        self.assertIsInstance(instance.thing, test_models.ModelWithForeignKey)
        self.assertIsInstance(instance.thing.thing,
                test_models.ModelReferencedByForiegnKeyField)

    def test_make_one_makes_fk_for_every_self_needed_for_m2m(self):
        # Where a model with a self m2m field has a foriegn key,
        # instances are created for that foreign key for every
        # self instance created
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithForeignKeyAndSelfManyToMany)
        self.assertIsInstance(instance,
                test_models.ModelWithForeignKeyAndSelfManyToMany)
        self.assertIsInstance(instance.thing,
                test_models.ModelReferencedByForiegnKeyField)
        self.assertEqual(1, instance.selves.count())
        self.assertIsInstance(instance.selves.get(),
                test_models.ModelWithForeignKeyAndSelfManyToMany)
        self.assertIsInstance(instance.selves.get().thing,
                test_models.ModelReferencedByForiegnKeyField)

    def test_make_one_passes_attrs_to_instance_generator(self):
        # Any factory instance generator gets passed the attrs passed to
        # make_one so that it can used them when generating the
        # instance.
        expected_value = 'AAAAA'
        factory = Factory()
        instance = factory.make_one(test_models.ModelWithInstanceGenerator,
                char_field=expected_value)
        self.assertEqual(expected_value, instance.char_field)

    def test_make_one_uses_any_model_generators_entry(self):
        # If there is a model_generators entry for the model being
        # generated then it is used.
        model = test_models.ModelWithCharField
        expected_value = model(char_field=self.getUniqueString())
        def make_value(factory, **attrs):
            return expected_value
        factory = Factory(model_generators={model: make_value})
        instance = factory.make_one(model)
        self.assertIs(expected_value, instance)

    def test_make_makes_many(self):
        factory = Factory()
        count = 5
        instances = factory.make(count, test_models.ModelWithNoFields)
        self.assertEqual(count, len(instances))

    def test_make_saves(self):
        factory = Factory()
        count = 5
        instances = factory.make(count, test_models.ModelWithNoFields)
        self.assertEqual(count,
                test_models.ModelWithNoFields.objects.all().count())

    def test_prepare_makes_many(self):
        factory = Factory()
        count = 5
        instances = factory.prepare(count, test_models.ModelWithNoFields)
        self.assertEqual(count, len(instances))

    def test_prepare_doesnt_save(self):
        factory = Factory()
        count = 5
        instances = factory.prepare(count, test_models.ModelWithNoFields)
        self.assertEqual(0,
                test_models.ModelWithNoFields.objects.all().count())

    def test_get_unique_integer_is_integer(self):
        factory = Factory()
        self.assertIsInstance(factory.getUniqueInteger(), int)

    def test_get_unique_integer_is_unique(self):
        factory = Factory()
        self.assertNotEquals(factory.getUniqueInteger(),
                factory.getUniqueInteger())

    def test_get_unique_string_is_str(self):
        factory = Factory()
        self.assertIsInstance(factory.getUniqueString(), str)

    def test_get_unique_string_is_unique(self):
        factory = Factory()
        self.assertNotEquals(factory.getUniqueString(),
                factory.getUniqueString())

    def test_get_unique_string_uses_prefix(self):
        factory = Factory()
        prefix = self.getUniqueString()
        self.assertThat(factory.getUniqueString(prefix=prefix),
                StartsWith(prefix))

    def test_get_unique_unicode_is_unicode(self):
        factory = Factory()
        self.assertIsInstance(factory.getUniqueUnicode(), unicode)

    def test_get_unique_unicode_is_unique(self):
        factory = Factory()
        self.assertNotEquals(factory.getUniqueUnicode(),
                factory.getUniqueUnicode())

    def test_get_unique_unicode_uses_prefix(self):
        factory = Factory()
        prefix = self.getUniqueString()
        self.assertThat(factory.getUniqueUnicode(prefix=prefix),
                StartsWith(prefix))

    def test_get_unique_date_is_date(self):
        factory = Factory()
        self.assertIsInstance(factory.getUniqueDate(), datetime.date)

    def test_get_unique_date_is_unique(self):
        factory = Factory()
        self.assertNotEquals(factory.getUniqueDate(), factory.getUniqueDate())

    def test_get_unique_datetime_is_datetime(self):
        factory = Factory()
        self.assertIsInstance(factory.getUniqueDateTime(), datetime.datetime)

    def test_get_unique_datetime_is_unique(self):
        factory = Factory()
        self.assertNotEquals(factory.getUniqueDateTime(), factory.getUniqueDateTime())

    def test_get_unique_time_is_time(self):
        factory = Factory()
        self.assertIsInstance(factory.getUniqueTime(), datetime.time)

    def test_get_unique_time_is_unique(self):
        factory = Factory()
        self.assertNotEquals(factory.getUniqueTime(), factory.getUniqueTime())

    def test__get_references_to_too_many_references(self):
        factory = Factory()
        source_model = test_models.ThrougModelWithTwoReferences
        target_model = test_models.ModelReferencingSelfWithThrough
        e = self.assertRaises(exceptions.ImproperlyConfigured,
                factory._get_references_to, source_model, target_model,
                'things', target_model)
        self.assertThat(str(e),
            StartsWith("Two references to %r from %r"
                % (target_model, source_model)))


class TestDummyTestCase(TestCase):

    def test_get_unique_integer_is_integer(self):
        dummy = DummyTestCase()
        self.assertIsInstance(dummy.getUniqueInteger(), int)

    def test_get_unique_integer_is_unique(self):
        dummy = DummyTestCase()
        self.assertNotEquals(dummy.getUniqueInteger(), dummy.getUniqueInteger())

    def test_get_unique_str_is_str(self):
        dummy = DummyTestCase()
        self.assertIsInstance(dummy.getUniqueString(), str)

    def test_get_unique_str_is_unique(self):
        dummy = DummyTestCase()
        self.assertNotEquals(dummy.getUniqueString(), dummy.getUniqueString())

    def test_get_unique_str_uses_prefix(self):
        dummy = DummyTestCase()
        prefix = self.getUniqueString()
        self.assertThat(dummy.getUniqueString(prefix=prefix), StartsWith(prefix))


class TestTestCases(TestCase):

    def run_test(self, cls, method_name):
        test = cls(method_name)
        result = ExtendedToOriginalDecorator(TestResult())
        result.startTestRun()
        # Note that test.run() can't be used here, as django does setup
        # in __call__.
        test(result)
        result.stopTestRun()
        return result

    def test_test_case(self):
        class Test(testcase.TestCase):
            def test_foo(self):
                self.assertIsInstance(self.factory, Factory)
        result = self.run_test(Test, 'test_foo')
        self.assert_(result.wasSuccessful(), result.errors or result.failures)

    def test_transaction_test_case(self):
        class Test(testcase.TransactionTestCase):
            def test_foo(self):
                self.assertIsInstance(self.factory, Factory)
        result = self.run_test(Test, 'test_foo')
        self.assert_(result.wasSuccessful(), result.errors or result.failures)

    def test_test_case_get_unique_integer(self):
        class Test(testcase.TestCase):
            def test_foo(self):
                self.getUniqueInteger()
        result = self.run_test(Test, 'test_foo')
        self.assert_(result.wasSuccessful(), result.errors or result.failures)

    def test_transaction_test_case_get_unique_integer(self):
        class Test(testcase.TransactionTestCase):
            def test_foo(self):
                self.getUniqueInteger()
        result = self.run_test(Test, 'test_foo')
        self.assert_(result.wasSuccessful(), result.errors or result.failures)

    def test_test_case_make_user_default_password(self):
        class Test(testcase.TestCase):
            def test_user_default_password(self):
                user = self.factory.make_one(User)
                logged_in = self.client.login(username=user.username,
                                                    password='test')
                self.assertTrue(logged_in)
        result = self.run_test(Test, 'test_user_default_password')
        self.assert_(result.wasSuccessful(), result.errors or result.failures)

    def test_test_case_make_user_explicit_password(self):
        class Test(testcase.TestCase):
            def test_user_explicit_password(self):
                user = self.factory.make_one(User,
                                             password='mypassword')
                logged_in = self.client.login(username=user.username,
                                              password='mypassword')
                self.assertTrue(logged_in)
        result = self.run_test(Test, 'test_user_explicit_password')
        self.assert_(result.wasSuccessful(), result.errors or result.failures)
