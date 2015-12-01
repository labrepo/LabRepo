# -*- coding: utf-8 -*-
import json
import os

from django.conf import settings

import elasticutils
from elasticutils.utils import chunked
from celery.task import task


@task
def index_objects(mapping_type, ids, chunk_size=100, es=None, index=None):
    if settings.ES_DISABLED:
        return

    create_mapping(mapping_type)
    # Get the model this mapping type is based on.
    model = mapping_type.get_model()
    # Retrieve all the objects that we're going to index and do it in
    # bulk.
    for id_list in chunked(ids, chunk_size):
        documents = []

        for obj in model.objects.filter(id__in=id_list):
            try:
                doc = mapping_type.extract_document(obj.id, obj)
                if isinstance(doc, list):
                    documents.extend(doc)
                else:
                    documents.append(doc)
            except StandardError as exc:
                print 'Unable to extract document {0}: {1}'.format(obj, repr(exc))

        if documents:
            mapping_type.bulk_index(documents, id_field='id', es=es, index=index)


@task
def unindex_objects(mapping_type, ids, es=None, index=None):
    """Remove documents of a specified mapping_type from the index.

    This allows for asynchronous deleting.

    If a mapping_type extends Indexable, you can add a ``pre_delete``
    hook for the model that it's based on like this::

        @receiver(dbsignals.pre_delete, sender=MyModel)
        def remove_from_index(sender, instance, **kw):
            from elasticutils.contrib.django import tasks
            tasks.unindex_objects.delay(MyMappingType, [instance.id])

    :arg mapping_type: the mapping type for these ids
    :arg ids: the list of ids of things to remove
    :arg es: The `Elasticsearch` to use. If you don't specify an
        `Elasticsearch`, it'll use `mapping_type.get_es()`.
    :arg index: The name of the index to use. If you don't specify one
        it'll use `mapping_type.get_index()`.
    """
    if settings.ES_DISABLED:
        return

    for id_ in ids:
        mapping_type.unindex(id_, es=es, index=index)


def create_mapping(mapping_type):
    #create map
    os.system('curl -XPUT {}/{} -d \'{}\''.format(settings.ES_URLS[0], settings.ES_INDEXES['default'],
                                                  json.dumps(mapping_type.get_mapping())))
