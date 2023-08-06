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

import django
from django.core.exceptions import ImproperlyConfigured
from django.db.models import fields as django_fields, ForeignKey, ManyToManyField
from django_factory import generators

__all__ = [
    'Factory',
    ]


class DummyTestCase(object):
    """A TestCase placeholder with the required methods.

    If the developer doesn't pass in a TestCase instance to the factory
    then we have to use something else to get unique values. This is
    that thing.
    """

    def __init__(self):
        self.counter = 0

    def getUniqueInteger(self):
        self.counter += 1
        return self.counter

    def getUniqueString(self, prefix=None):
        if prefix is None:
            prefix = ""
        return "%sstr-%d" % (prefix, self.getUniqueInteger())


def get_from_choices(choices):
    """Pick a value from the choices for a particular field."""
    return choices[0][0]


class Factory(object):

    # The name of the nested class that will be used to find any
    # generator functions for a model or its fields.
    MODEL_FACTORY_CLASS_NAME = 'Factory'

    # The default mapping from Fields to the functions that will
    # generate values for that field when needed.
    DEFAULT_FIELD_MAPPING = {
        django_fields.BooleanField: generators.generate_boolean,
        django_fields.NullBooleanField: generators.generate_boolean,

        django_fields.IntegerField: generators.generate_int,
        django_fields.SmallIntegerField: generators.generate_int,
        django_fields.PositiveIntegerField: generators.generate_int,
        django_fields.PositiveSmallIntegerField: generators.generate_int,
        django_fields.FloatField: generators.generate_float,
        django_fields.DecimalField: generators.generate_decimal,

        django_fields.CharField: generators.generate_unicode,
        django_fields.TextField: generators.generate_unicode,
        django_fields.SlugField: generators.generate_unicode,

        django_fields.DateField: generators.generate_date,
        django_fields.DateTimeField: generators.generate_datetime,
        django_fields.TimeField: generators.generate_time,

        django_fields.URLField: generators.generate_url,
        django_fields.EmailField: generators.generate_email,

        django_fields.CommaSeparatedIntegerField: generators.generate_comma_separated_integer,
        django_fields.IPAddressField: generators.generate_ip_address,

        django_fields.files.FileField: generators.generate_file,
        django_fields.files.ImageField: generators.generate_file,

        # TODO: FilePathField
        }

    # GenericIPAddressField is new in Django 1.4, so only reference it
    # if available.
    if getattr(django_fields, 'GenericIPAddressField', None) is not None:
        DEFAULT_FIELD_MAPPING[django_fields.GenericIPAddressField] = generators.generate_generic_ip_address

    # BigIntegerField is new in Django 1.2, so only reference it
    # if available.
    if getattr(django_fields, 'BigIntegerField', None) is not None:
        DEFAULT_FIELD_MAPPING[django_fields.BigIntegerField] = generators.generate_int

    DEFAULT_MODEL_GENERATORS = {}

    def __init__(self, test_case=None, field_mapping=None,
                 model_generators=None):
        """Create a Factory.

        :param test_case: a testtools.TestCase instance that should be used
            to get unique values when needed. May be None to generate unique
            values internally.
        :param field_mapping: the mapping from Field to function to generate
            values for that field to use in this factory. May be None
            to use the default mapping.
        :param model_generators: the mapping from Model to function to generate
            instances of that model to use in this factory. May be None
            to use the default mapping.
        """
        self.test_case = test_case or DummyTestCase()
        self.field_mapping = field_mapping or self.DEFAULT_FIELD_MAPPING.copy()
        self.model_generators = model_generators or self.DEFAULT_MODEL_GENERATORS.copy()

    def _get_model_factory_attribute(self, model, attr):
        """Get an attribute from ``model``'s nested Factory class, if any.

        :param model: the model to take the Factory class and attribute from.
        :param attr: the name of the attribute to receive.
        :return: the attribute or None.
        """
        model_factory = getattr(model, self.MODEL_FACTORY_CLASS_NAME, None)
        if model_factory:
            return getattr(model_factory, attr, None)
        return None

    def _get_instance_from_factory(self, model, attrs):
        """Get an instance from any factory instance generator on the model.

        :param model: the model to generate an instance for.
        :param attrs: the key/value dict containing developer-specified
            values for the instance attributes.
        :return: an instance of the model if the model's Factory nested
            class has an instance generator, or None if it does not.
        """
        instance = None
        instance_generator = self._get_model_factory_attribute(model,
                'make_instance')
        if instance_generator is not None:
            instance = instance_generator(self, **attrs)
        return instance

    def _number_of_many_to_many_to_make(self, model, field):
        """Returns the number of instances of a ManyToManyField target to make.

        Any factory nested class on the model will be consulted for an
        attribute specifying the number of instances to create. If the
        attribute is present then it will be returned or called as
        appropriate. If it is not present then the default value will be used.

        :param model: the model to check for a nested class property
                specifying the number of instances to create.
        :param field: the field that the value should correspond to.
        :return: an integer specifying the number of instances to create.
        """
        count = self._get_model_factory_attribute(model,
                "number_of_" + field.name)
        if count is not None:
            if callable(count):
                return count()
            else:
                return count
        return 1

    def _generate_many_to_many_value(self, model, field, not_including, attrs):
        """Generate a value for a ManyToManyField.

        :param model: the model that the field is being populated for.
        :param field: the particular field that the value is for.
        :param not_including: a list of Models that no value should be
                generated for in order to break loops.
        :param attrs: the key/value dict of developer-supplied values for the
                main instance.
        :return: a tuple of ``(generated, value)`` where ``generated`` is a
                boolean specifying whether any value was actually generated,
                and ``value`` is the generated value if ``generated`` is
                ``True``.
        """
        if field.name in attrs:
            return True, attrs.pop(field.name)
        else:
            if field.related.parent_model in not_including:
                return False, None
            has_factory, value = self._get_value_from_model_factory(model, field)
            if not has_factory:
                if field.null:
                    return False, None
                count = self._number_of_many_to_many_to_make(model, field)
                value = []
                for i in range(count):
                    value.append(self._create_one(field.related.parent_model, True,
                        not_including + [model], {}))
            return True, value

    def _generate_foreign_key_value(self, model, field, not_including, attrs):
        """Generate a value for a ForeignKey.

        :param model: the model that the field is being populated for.
        :param field: the particular field that the value is for.
        :param not_including: a list of Models that no value should be
                generated for in order to break loops.
        :param attrs: the key/value dict of developer-supplied values for the
                main instance.
        :return: a tuple of ``(generated, value)`` where ``generated`` is a
                boolean specifying whether any value was actually generated,
                and ``value`` is the generated value if ``generated`` is
                ``True``.
        """
        if field.name in attrs:
            return attrs[field.name] is not None, attrs.pop(field.name)
        else:
            if field.related.parent_model in not_including:
                return False, None
            has_factory, value = self._get_value_from_model_factory(model, field)
            if not has_factory:
                if field.blank and field.null:
                    return False, None
                # TODO: content types, maybe using a factory override
                #       for the model?
                value = self._create_one(field.related.parent_model, True,
                        not_including + [model], {})
            return True, value

    def _generate_plain_value(self, model, field, attrs):
        """Generate a value for a plain (non-reference) field..

        :param model: the model that the field is being populated for.
        :param field: the particular field that the value is for.
        :param attrs: the key/value dict of developer-supplied values for the
                main instance.
        :return: a tuple of ``(generated, value)`` where ``generated`` is a
                boolean specifying whether any value was actually generated,
                and ``value`` is the generated value if ``generated`` is
                ``True``.
        """
        if field.name in attrs:
            return False, None
        has_factory, value = self._get_value_from_model_factory(model, field)
        if not has_factory:
            if field.blank and field.null:
                return False, None
            if field.has_default():
                if callable(field.default):
                    value = field.default()
                else:
                    value = field.default
            else:
                value = self.generate_value(field)
        return True, value

    def _generate_instance(self, model, save, attrs, not_including):
        """Generate an instance of a model.

        :param model: the model that an instance should be generated for.
        :param attrs: the key/value dict of developer-supplied values for the
                instance attributes.
        :param not_including: a list of Models that no value should be
                generated for in order to break loops.
        :return: a tuple of ``(instance, many_to_may_dict, foreign_key_dict)``
                where ``instance`` is the generated instance,
                ``many_to_may_dict`` is a dict mapping from field name to
                list of instances for any ManyToManyFields and
                ``foreign_key_dict`` is a dict mapping from field name to
                instance for any ForeignKeys.
        """
        m2m_dict = {}
        fk_dict = {}
        fields = self.get_fields(model)
        for field in fields:
            if isinstance(field, ManyToManyField):
                if not save:
                    # When not saving the other instances aren't used so
                    # skip creating them.
                    continue
                use, value = self._generate_many_to_many_value(
                        model, field, not_including, attrs)
                if use:
                    m2m_dict[field.name] = value
            elif isinstance(field, ForeignKey):
                if not save:
                    # When not saving the other instances aren't used so
                    # skip creating them.
                    continue
                use, value = self._generate_foreign_key_value(
                        model, field, not_including, attrs)
                if use:
                    fk_dict[field.name] = value
            else:
                use, value = self._generate_plain_value(model, field, attrs)
                if use:
                    attrs[field.name] = value
        return model(**attrs), m2m_dict, fk_dict

    def _get_references_to(self, source_model, primary_model, field_name,
            secondary_model):
        """Get the foreign key fields referencing particular models.

        Given a source model and a primary and secondary target model,
        this method will return a tuple of the ForeignKey fields on the
        source model that reference the target models.

        :param source_model: the model to find the fields on.
        :param primary_model: the model that an instance is being
            generated for.
        :param field_name: the name of the ManyToManyField on the primary
            model that is being considered.
        :param secondary_model: the model that is the other side of the
            ManyToManyField.
        :return: a tuple of fields from source_model that refer to the target
                models, in the order (primary_model, secondary_model)
        :raises ImproperlyConfigured: if any target model is not referenced,
             or is referenced twice.
        """
        target_fields = [None, None]
        for field in self.get_fields(source_model):
            if isinstance(field, ForeignKey):
                for i, model in enumerate([primary_model, secondary_model]):
                    if field.related.parent_model == model:
                        if target_fields[i] is not None:
                            # FIXME: it would be nice to have a better
                            #        solution that having the developer
                            #        handle these cases by creating the
                            #        relations themselves.
                            raise ImproperlyConfigured(
                                ("Two references to %r from %r. The sematics "
                                 "of this relation are opaque to this code, "
                                 "so you must set number_of_%s = 0 on the "
                                 "Factory of %s and create the relationships "
                                 "youself.") % (model, source_model,
                                     field_name, primary_model))
                        target_fields[i] = field
        return target_fields

    def _generate_through_model_instances(self, through, instance,
            related_instances, not_including, field_name):
        """Generate instances of a through model for a ManyToManyField.

        When a ManyToManyField has a through model, relationships must be
        created by instantiating that through model. This method will
        create a number of instances of a through model given an instance
        of one side of the relationsip, and a list of instances of the
        other side. It will take care to set the appropriate attributes
        on the through model, regardless of their names, and generate
        values for any extra fields on the through model as needed.

        :param through: the intermediate model to create instances of.
        :param instance: the instance of one side of the relationship.
        :param related_instances: a list of instances of the other
            side of the relationship.
        :param not_including: a list of models to not create instances
            of when generating values for any extra fields on the
            through model.
        :param field_name: the name of the field on instance that
            the relations are being generated for.
        :return: None
        """
        if len(related_instances) < 1:
            return
        back_model = instance.__class__
        other_side_model = related_instances[0].__class__
        back_field, other_side_field = self._get_references_to(
                through, back_model, field_name, other_side_model)
        for related_instance in related_instances:
            self._create_one(through, True, not_including,
                    {back_field.name: instance,
                        other_side_field.name: related_instance})

    def _get_instance_from_model_generators(self, model, attrs):
        """Get an instance of ``model`` from the model_generators

        If ``model`` appears in model_generators use the generator
        from the mapping to create an instance of the model.
        The generator is passed the factory instance as the
        first parameter, and the attrs dict the develop
        supplied as **kwargs.

        :param model: the model to generate an instance of.
        :param attrs: the key/value dict the developer supplied to
            use as attributes on the generated model.
        :return: an instance of ``model`` or None if the
            model wasn't present in the model_generators.
        """
        if model in self.model_generators:
            return self.model_generators[model](self, **attrs)
        return None

    def _create_one(self, model, save, not_including, attrs):
        """Create one instance of a model, and optionally save it.

        :param model: the model that an instance should be generated for.
        :param save: whether to save the resulting instance.
        :param not_including: a list of Models that no value should be
                generated for in order to break loops.
        :param attrs: the key/value dict of developer-supplied values for the
                instance attributes.
        :return: the created instance.
        """
        m2m_dict = {}
        fk_dict = {}
        # XXX: do we have to pass ``save`` to the model_generators and
        # factory?
        instance = self._get_instance_from_model_generators(model, attrs)
        if instance is None:
            instance = self._get_instance_from_factory(model, attrs)
        if instance is None:
            instance, m2m_dict, fk_dict = self._generate_instance(model, save, attrs, not_including)
        if save:
            for key, model_instance in fk_dict.items():
                model_instance.save()
                setattr(instance, key, model_instance)

            instance.save()

            for key, value in m2m_dict.items():
                if len(value) < 1:
                    break
                instance_relation = getattr(instance, key)
                through_model = None
                if django.VERSION < (1, 2):
                    if instance_relation.through is not None:
                        through_model = instance_relation.instance._meta.get_field(key).rel.through_model
                else:
                    if not instance_relation.through._meta.auto_created:
                        through_model = instance_relation.through
                if through_model is None:
                    for model_instance in value:
                        model_instance.save()
                        instance_relation.add(model_instance)
                else:
                    self._generate_through_model_instances(
                            through_model, instance, value,
                            not_including, key)
            if getattr(instance, 'full_clean', None) is not None:
                instance.full_clean()
        return instance

    def _many(self, count, method, model, attrs):
        """Create a number of instances using the provided method."""
        instances = []
        for i in range(count):
            instances.append(method(model, **attrs))
        return instances

    def make(self, count, model, **attrs):
        """Make a configurable number of instances of ``model``.

        :param count: the number of instances to make
        :type count: int
        :param model: the model to create instances of
        :type model: ``Model``
        :param **kwargs: any attribute values to set to known values.
        :return: a list of created instances, the length of which
                will equal ``count``. All instances will be saved and
                have attributes defined by ``attrs``.
        """
        return self._many(count, self.make_one, model, attrs)

    def prepare(self, count, model, **attrs):
        """Prepare a configurable number of instances of ``model``.

        Note that ManyToManyFields and ForeignKeys will be
        None, as they can't be added unless the instance is saved.
        You will have to create instances of the referenced models
        and assign them to attributes as needed.

        :param count: the number of instances to prepare
        :type count: int
        :param model: the model to prepare instances of
        :type model: ``Model``
        :param **kwargs: any attribute values to set to known values.
        :return: a list of created instances, the length of which
                will equal ``count``. All instances will not be saved
                and have attributes defined by ``attrs``.
        """
        return self._many(count, self.prepare_one, model, attrs)

    def make_one(self, model, **attrs):
        """Make an instance of ``model``.

        :param model: the model to make instances of
        :type model: ``Model``
        :param **kwargs: any attribute values to set to known values.
        :return: an instance of ``model``.  The instance will be saved
                and have attributes defined by ``attrs``.
        """
        return self._create_one(model, True, [], attrs)

    def prepare_one(self, model, **attrs):
        """Prepare an instance of ``model``.

        Note that ManyToManyFields and ForeignKeys will be
        None, as they can't be added unless the instance is saved.
        You will have to create instances of the referenced models
        and assign them to attributes as needed.

        :param model: the model to prepare instances of
        :type model: ``Model``
        :param **kwargs: any attribute values to set to known values.
        :return: an instance of ``model``.  The instance will not be saved
                and have attributes defined by ``attrs``.
        """
        return self._create_one(model, False, [], attrs)

    def _get_value_from_model_factory(self, model, field):
        """Get the value for a field from a factory generator, if any.

        If the model has a factory generator for the field, then
        call it to get the value that should be used.

        :param model: the model to check the factory nested class of.
        :param field: the field that the value should be generated for.
        :return: a tuple of (``generated``, ``value``) where ``generated``
                is a boolean specifying whether a function was present,
                and ``value`` will be the generated value if ``generated``
                is ``True``.
        """
        generator = self._get_model_factory_attribute(model,
                "get_" + field.name)
        if generator:
            return True, generator(field, self)
        return False, None

    def generate_value(self, field):
        """Generate a value for ``field`` on ``model``.

        This method will generate a value for ``field`` depending
        on its type, and any attributes it has (such as ``choices``.)
        It does not obey any model factory nested class, or
        attributes such as ``default`` or ``null``.

        :param field: the field instance to generate the value for.
        :return: the value that should be used.
        :raises TypeError: if no generator is registered for the
            type of ``field``.
        """
        if getattr(field, 'choices'):
            generator = lambda x, y: get_from_choices(field.flatchoices)
        else:
            generator = self.field_mapping.get(field.__class__)
        if generator is None:
            raise TypeError("Can't generate value for field: %s" % field)
        return generator(field, self)

    @staticmethod
    def get_fields(model):
        """Get the fields of ``model`` filtering any automatic fields.

        :param model: the Model to get the fields of.
        :return: a list of field instances, not including any ``AutoField``.
        """
        fields = model._meta.fields[:] + model._meta.many_to_many[:]
        for field in fields[:]:
            # TODO: filter GenericRelation
            if isinstance(field, django_fields.AutoField):
                fields.remove(field)
        return fields

    def getUniqueInteger(self):
        """Get a unique integer.

        The value will be unique for this factory.

        :return_type: int
        """
        return self.test_case.getUniqueInteger()

    def getUniqueString(self, prefix=None):
        """Get a unique string.

        The value will be unique for this factory.

        :return_type: str
        """
        return self.test_case.getUniqueString(prefix=prefix)

    def getUniqueUnicode(self, prefix=None):
        """Get a unique unicode string.

        The value will be unique for this factory.

        :return_type: unicode
        """
        return self.getUniqueString(prefix=prefix).decode("utf-8")

    def getUniqueDate(self):
        """Get a unique date.

        The value will be unique for this factory.

        :return_type: datetime.date
        """
        start_date = datetime.date(2000, 1, 1)
        return start_date + datetime.timedelta(days=self.getUniqueInteger())

    def getUniqueDateTime(self):
        """Get a unique datetime.

        The value will be unique for this factory.

        :return_type: datetime.datetime
        """
        start_date = datetime.datetime(1970, 1, 1)
        return start_date + datetime.timedelta(days=self.getUniqueInteger())

    def getUniqueTime(self):
        """Get a unique time.

        The value will be unique for this factory.

        :return_type: datetime.time
        """
        start_date = self.getUniqueDateTime()
        return (start_date + datetime.timedelta(minutes=self.getUniqueInteger())).time()
