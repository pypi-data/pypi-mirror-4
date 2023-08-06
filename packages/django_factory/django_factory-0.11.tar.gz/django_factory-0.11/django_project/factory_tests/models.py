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

from django.core import exceptions
from django.db import models


class ModelWithNoFields(models.Model):
    pass


class ModelWithCharField(models.Model):

    char_field = models.CharField(max_length=100)


class ModelWithNullAndBlankCharField(models.Model):

    char_field = models.CharField(max_length=100, null=True, blank=True)


class ModelWithNullCharField(models.Model):

    char_field = models.CharField(max_length=100, null=True)


class ModelWithBlankCharField(models.Model):

    char_field = models.CharField(max_length=100, blank=True)


class ModelWithMaxLengthCharField(models.Model):

    char_field = models.CharField(max_length=5)


class ModelWithNullAndBlankCharFieldAndFactory(models.Model):

    VALUE = 'bar'

    char_field = models.CharField(max_length=100, null=True, blank=True)

    class Factory:

        @staticmethod
        def get_char_field(field, factory):
            return ModelWithNullAndBlankCharFieldAndFactory.VALUE


class ModelWithDefaultCharField(models.Model):

    DEFAULT = 'foo'

    char_field = models.CharField(max_length=100, default=DEFAULT)


class ModelWithDefaultCharFieldAndFactory(models.Model):

    VALUE = 'bar'
    DEFAULT = 'foo'

    char_field = models.CharField(max_length=100, default=DEFAULT)

    class Factory:

        @staticmethod
        def get_char_field(field, factory):
            return ModelWithDefaultCharFieldAndFactory.VALUE


class ModelWithCallableDefaultCharField(models.Model):

    DEFAULT = 'foo'

    def get_default():
        return ModelWithCallableDefaultCharField.DEFAULT

    char_field = models.CharField(max_length=100, default=get_default)


class ModelWithTextField(models.Model):

    text_field = models.TextField(max_length=100)


class ModelWithNoneMaxLengthTextField(models.Model):

    text_field = models.TextField(max_length=None)


class ModelWithSlugField(models.Model):

    slug_field = models.SlugField(max_length=100)


class ModelWithBooleanField(models.Model):

    bool_field = models.BooleanField()


class ModelWithNullBooleanField(models.Model):

    bool_field = models.NullBooleanField()


class ModelWithIntegerField(models.Model):

    int_field = models.IntegerField()


if getattr(models, 'BigIntegerField', None) is not None:
    class ModelWithBigIntegerField(models.Model):

        big_int_field = models.BigIntegerField()


class ModelWithSmallIntegerField(models.Model):

    small_int_field = models.SmallIntegerField()


class ModelWithPositiveIntegerField(models.Model):

    positive_int_field = models.PositiveIntegerField()


class ModelWithPositiveSmallIntegerField(models.Model):

    positive_small_int_field = models.PositiveSmallIntegerField()


class ModelWithFloatField(models.Model):

    float_field = models.FloatField()


class ModelWithDecimalField(models.Model):

    decimal_field = models.DecimalField(decimal_places=2, max_digits=3)


class ModelWithDateField(models.Model):

    date_field = models.DateField()


class ModelWithDateTimeField(models.Model):

    datetime_field = models.DateTimeField()


class ModelWithTimeField(models.Model):

    time_field = models.TimeField()


class ModelWithURLField(models.Model):

    url_field = models.URLField()


class ModelWithEmailField(models.Model):

    email_field = models.EmailField()


class ModelWithCommaSeparatedIntegerField(models.Model):

    csi_field = models.CommaSeparatedIntegerField(max_length=6)


class ModelWithIPAddressField(models.Model):

    ip_field = models.IPAddressField()


if getattr(models, 'GenericIPAddressField', None) is not None:
    class ModelWithGenericIPAddressField(models.Model):

        ip_field = models.GenericIPAddressField()


class ModelWithFileField(models.Model):

    file_field = models.FileField(upload_to='foo')


class ModelWithImageField(models.Model):

    image_field = models.ImageField(upload_to='foo')


class ModelWithChoices(models.Model):

    CHOICES = [(-1, 'foo'), (-2, 'bar')]

    choices_field = models.IntegerField(choices=CHOICES)


class ModelWithChoiceGroups(models.Model):

    CHOICES = [('foo', ((-1, 'foo'), )), ('bar', ((-2, 'bar'), ))]

    choices_field = models.IntegerField(choices=CHOICES)


class ModelWithFieldGenerator(models.Model):

    VALUE = 'bar'

    char_field = models.CharField(max_length=100)

    class Factory:

        @staticmethod
        def get_char_field(field, factory):
            return ModelWithFieldGenerator.VALUE


class ModelWithInstanceGenerator(models.Model):

    VALUE = 'bar'

    char_field = models.CharField(max_length=100)

    class Factory:

        @staticmethod
        def make_instance(factory, char_field=None):
            if char_field is None:
                char_field = ModelWithInstanceGenerator.VALUE
            return ModelWithInstanceGenerator(char_field=char_field)


class ModelReferencedByManyToManyField(models.Model):
    pass


class ModelWithManyToManyField(models.Model):

    things = models.ManyToManyField(ModelReferencedByManyToManyField)


class ModelWithManyToManyFieldAndFactory(models.Model):

    VALUE = ModelReferencedByManyToManyField()

    things = models.ManyToManyField(ModelReferencedByManyToManyField)

    class Factory:

        @staticmethod
        def get_things(field, factory):
            return [ModelWithManyToManyFieldAndFactory.VALUE]


class ModelWithNullManyToManyField(models.Model):

    things = models.ManyToManyField(ModelReferencedByManyToManyField, null=True)


class ModelWithNullManyToManyFieldAndFactory(models.Model):

    VALUE = ModelReferencedByManyToManyField()

    things = models.ManyToManyField(ModelReferencedByManyToManyField, null=True)

    class Factory:

        @staticmethod
        def get_things(field, factory):
            return [ModelWithNullManyToManyFieldAndFactory.VALUE]


class ModelWithSelfManyToManyField(models.Model):

    # Not symetrical so we can tell which is the child
    things = models.ManyToManyField('self', symmetrical=False)


class ModelWithCircularReferenceLoop1(models.Model):

    things = models.ManyToManyField('ModelWithCircularReferenceLoop2')


class ModelWithCircularReferenceLoop2(models.Model):

    other_things = models.ManyToManyField('ModelWithCircularReferenceLoop1')


class ModelWantingTwoManyToManyInstances(models.Model):

    things = models.ManyToManyField(ModelReferencedByManyToManyField)

    class Factory:
        number_of_things = 2


class ModelWantingZeroManyToManyInstances(models.Model):

    things = models.ManyToManyField(ModelReferencedByManyToManyField)

    class Factory:
        number_of_things = 0


class ModelWithCallableSpecifiedManyToManyField(models.Model):

    COUNT = 2

    things = models.ManyToManyField(ModelReferencedByManyToManyField)

    class Factory:

        @staticmethod
        def number_of_things():
            return ModelWithCallableSpecifiedManyToManyField.COUNT


###
# We break the naming convention for these models so the created
# attributes have reasonable names
class Person(models.Model):
    pass


class Membership(models.Model):

    person = models.ForeignKey(Person)
    group = models.ForeignKey('Group')
    comment = models.CharField(max_length=100)


class Group(models.Model):

    people = models.ManyToManyField(Person, through=Membership)
###


class ThrougModelWithTwoReferences(models.Model):

    one = models.ForeignKey('ModelReferencingSelfWithThrough',
            related_name="ones")
    two = models.ForeignKey('ModelReferencingSelfWithThrough',
            related_name="twos")


class ModelReferencingSelfWithThrough(models.Model):

    things = models.ManyToManyField('self',
            through=ThrougModelWithTwoReferences, symmetrical=False)


class ModelReferencedByForiegnKeyField(models.Model):
    pass


class ModelWithForeignKey(models.Model):

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField)


class ModelWithNullAndBlankForeignKey(models.Model):

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField, null=True, blank=True)


class ModelWithNullForeignKey(models.Model):

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField, null=True)


class ModelWithBlankForeignKey(models.Model):

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField, blank=True)


class ModelWithForeignKeyAndFactory(models.Model):

    VALUE = ModelReferencedByForiegnKeyField()

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField)

    class Factory:

        @staticmethod
        def get_thing(field, factory):
            return ModelWithForeignKeyAndFactory.VALUE


class ModelWithSelfForeignKey(models.Model):

    thing = models.ForeignKey('self', null=True, blank=True)


class ModelWithCircularForiegnKeyReferenceLoop1(models.Model):

    thing = models.ForeignKey('ModelWithCircularForiegnKeyReferenceLoop2')


class ModelWithCircularForiegnKeyReferenceLoop2(models.Model):

    thing = models.ForeignKey('ModelWithCircularForiegnKeyReferenceLoop1', null=True, blank=True)


class ModelWithForiegnKeyToModelWithForeignKey(models.Model):

    thing = models.ForeignKey(ModelWithForeignKey)


class ModelWithForeignKeyAndSelfManyToMany(models.Model):

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField)
    selves = models.ManyToManyField('self', symmetrical=False)


if getattr(models.CharField, 'default_validators', None) is not None:
    class ModelWithImpossibleValidator(models.Model):

        def impossible(value):
            raise exceptions.ValidationError('Impossible')

        char_field = models.CharField(max_length=100, validators=[impossible])
