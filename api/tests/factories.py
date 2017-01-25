# -*- coding: utf-8 -*-
import os
import random

import factory
import factory.fuzzy
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.files import File
from faker import Faker

from api.models import Station, Metering, MeteringHistory, Project


class AbstractLocationFactory(factory.django.DjangoModelFactory):

    @factory.lazy_attribute
    def position(self):
        x = random.uniform(14.12297069999998, 24.14578300000009)
        y = random.uniform(49.00204680000022, 54.83578869999986)
        return Point([x, y])

    country = 'Polska'
    state = factory.fuzzy.FuzzyChoice(['Małopolska', 'Wielkopolska'])
    county = factory.fuzzy.FuzzyChoice(['nowotomyski', 'krakowski'])
    community = factory.fuzzy.FuzzyChoice(['Nowy Tomyśl', 'Kraków'])
    city = factory.fuzzy.FuzzyChoice(['Nowy Tomyśl', 'Kraków'])
    district = factory.fuzzy.FuzzyChoice(['Kazmierz', 'Nowa Huta', 'Krowodrza'])

    class Meta:
        abstract = True


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.LazyFunction(lambda: 'smoglyuser-%s' % Faker().uuid4())
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')


class ProjectFactory(AbstractLocationFactory):
    name = factory.Sequence(lambda n: 'Smogly Project %04d' % n)
    website = factory.Sequence(lambda n: 'http://%04d.smogly.org' % n)
    description = factory.Faker('sentences', nb=3)
    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def logo(self, create, extracted, **kwargs):
        if not (extracted is False):
            if create:
                # add random image from factories assets
                source_file_name = 'logo{}.jpg'.format(random.randint(1, 4))
                source_path = os.path.join(
                    os.path.dirname(__file__),
                    'assets',
                    'project',
                    source_file_name
                )
                # save using ImageField
                destination_file_name = '%s.jpg' % Faker().uuid4()
                destination_path = os.path.join(
                    'project',
                    destination_file_name
                )
                self.logo.save(
                    destination_path,
                    File(
                        open(
                            source_path,
                            # for python 3.x, we need binary mode
                            # https://github.com/python-pillow/Pillow/issues/1605#issuecomment-167402651
                            'rb'
                        )
                    )
                )
                self.save(update_fields=['logo'])

    class Meta:
        model = Project


class StationFactory(AbstractLocationFactory):
    name = factory.Sequence(lambda n: 'Smogly Station %04d' % n)
    type = factory.fuzzy.FuzzyChoice([type_choice[0] for type_choice in Station.TYPE_CHOICES])
    notes = factory.Faker('sentences', nb=3)
    altitude = factory.fuzzy.FuzzyFloat(0.0, 40.0)
    project = factory.SubFactory(ProjectFactory, **{
        'position': factory.SelfAttribute('position'),
        'country': factory.SelfAttribute('country'),
        'state': factory.SelfAttribute('state'),
        'county': factory.SelfAttribute('county'),
        'community': factory.SelfAttribute('community'),
        'district': factory.SelfAttribute('district')
    })
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = Station


class AbstractMeteringFactory(factory.django.DjangoModelFactory):
    pm01 = factory.fuzzy.FuzzyFloat(0.0, 150.0)
    pm25 = factory.fuzzy.FuzzyFloat(0.0, 150.0)
    pm10 = factory.fuzzy.FuzzyFloat(0.0, 150.0)
    temp_out1 = factory.fuzzy.FuzzyFloat(-25.0, 30.0)
    temp_out2 = factory.SelfAttribute('temp_out1')
    temp_out3 = factory.SelfAttribute('temp_out1')
    temp_int_air1 = factory.fuzzy.FuzzyFloat(28.0, 30.0)
    hum_out1 = factory.fuzzy.FuzzyFloat(5.0, 99.0)
    hum_out2 = factory.SelfAttribute('hum_out1')
    hum_out3 = factory.SelfAttribute('hum_out1')
    hum_int_air1 = factory.fuzzy.FuzzyFloat(30.0, 35.0)
    rssi = factory.fuzzy.FuzzyFloat(-100.0, 0.0)
    bpress_out1 = factory.fuzzy.FuzzyFloat(900, 1100)

    station = factory.SubFactory(StationFactory)

    class Meta:
        abstract = True


class MeteringFactory(AbstractMeteringFactory):
    class Meta:
        model = Metering


class MeteringHistoryFactory(AbstractMeteringFactory):
    class Meta:
        model = MeteringHistory
