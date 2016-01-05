# -*- coding: utf-8 -*-
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from experiments.search_indexes import ExperimentMappingType
from comments.search_indexes import CommentMappingType
from profiles.search_indexes import ProfileMappingType
from units.search_indexes import UnitMappingType


class Command(BaseCommand):

    help = 'Used to create a elasticsearch index and create or update mapping types.'

    def handle(self, *args, **options):
        mapping_types = [ExperimentMappingType, UnitMappingType, CommentMappingType, ProfileMappingType]
        for mapping_type in mapping_types:
            os.system('curl -XPUT {}/{} -d \'{}\''.format(settings.ES_URLS[0], settings.ES_INDEXES['default'],
                                                          json.dumps(mapping_type.get_mapping())))
        self.stdout.write("Mapping types created successfully.")
        return