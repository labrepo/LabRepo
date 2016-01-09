from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.db.models import Q
from django import forms

from profiles.models import LabUser as User
from comments.search_indexes import CommentMappingType
from common.mixins import LoginRequiredMixin
from experiments.models import Experiment
from experiments.search_indexes import ExperimentMappingType
from labs.models import Lab
from profiles.search_indexes import ProfileMappingType
# from unit_collections.forms import CollectionForm, UpdateUnitsCollectionForm
from experiments.forms import UpdateUnitsForm
from units.search_indexes import UnitMappingType
from .forms import SearchForm, SimpleSearchForm


class ElasticSimpleSearchView(LoginRequiredMixin, TemplateResponseMixin, View):
    """
    View for full text search. Use the wildcard query is a low-level term-based query.
    It uses the standard shell wildcards where ? matches any character, and * matches zero or more characters.
    """
    template_name = 'search/search_list.html'
    form_class = SimpleSearchForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET)
        self.lab = Lab.objects.get(pk=self.kwargs['lab_pk'])
        if form.is_valid():
            query = []
            comments_query, units_query, profiles = [], [], []
            user = self.request.user

            for elastic_type, search_data in form.cleaned_data['q']:
                if elastic_type == '_all':
                    comments_query.append({"match": search_data})
                    units_query.append({"match": search_data})
                    # measurement_query.append({"match": search_data})
                    query.extend([
                        {
                            "filtered": {
                                "filter": {
                                    'or': [
                                        {
                                            "query": {
                                                "query_string": {
                                                    "query": search_data.values()[0]
                                                }
                                            }
                                        },
                                        {
                                            "has_child": {
                                                'type': UnitMappingType.get_mapping_type_name(),
                                                "query": {
                                                    "filtered": {
                                                        "query": {"match": search_data}
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "has_child": {
                                                'type': CommentMappingType.get_mapping_type_name(),
                                                "query": {
                                                    "filtered": {
                                                        "query": {"match": search_data}
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                    ])

            experiments = ExperimentMappingType.search()\
                .filter_raw({'term': {'lab.id': self.kwargs['lab_pk']}})\
                .query_raw({
                    "bool": {
                        "must": query
                    }
                })

            # check permission
            if self.lab.is_guest(user):
                experiments = Experiment.objects.filter(Q(id__in=[experiment.id for experiment in experiments], active=True) &
                                                        (Q(owners=user) | Q(editors=user) | Q(viewers=user)))
            experiment_ids = {
                'has_parent': {
                    "parent_type": ExperimentMappingType.get_mapping_type_name(),
                    "query": {
                        "ids": {"values": [unicode(experiment.id) for experiment in experiments]}
                    }
                }
            }

            units_query.append(experiment_ids)
            units = UnitMappingType.search()\
                .query_raw({
                    "bool": {
                        "must": units_query
                    }
                })

            unit_ids = {
                'has_parent': {
                    "parent_type": UnitMappingType.get_mapping_type_name(),
                    "query": {
                        "ids": {"values": [unit.id for unit in units]}
                    }
                }
            }
            # measurement_query.append(unit_ids)
            # measurements = MeasurementMappingType.search()\
            #     .query_raw({
            #         "bool": {
            #             "must": measurement_query
            #         }
            #     })

            comments_query.append(experiment_ids)
            comments = CommentMappingType.search()\
                .query_raw({
                    "bool": {
                        "must": comments_query
                    }
                })
            return self.render_to_response(self.get_context_data(experiments=experiments, units=units, profiles=profiles,
                                                                 comments=comments))
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        ctx = kwargs.copy()
        ctx['form'] = self.form_class(self.request.GET)
        # ctx['create_collection_form'] = CollectionForm(initial={'lab': self.lab, 'user': self.request.user})
        ctx['update_experiment_form'] = UpdateUnitsForm(initial={'lab': self.lab, 'user': self.request.user})
        return ctx


class ElasticSearchView(LoginRequiredMixin, TemplateResponseMixin, View):
    """
    View for full text search. Use the wildcard query is a low-level term-based query.
    It uses the standard shell wildcards where ? matches any character, and * matches zero or more characters.
    """
    template_name = 'search/search_list.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET)
        self.lab = Lab.objects.get(pk=self.kwargs['lab_pk'])
        if form.is_valid():
            query = []
            comments_query, units_query, profiles = [], [], []
            user = self.request.user
            for elastic_type, search_data in form.cleaned_data['q']:
                if elastic_type == 'comment':
                    comments_query.append({"wildcard": search_data})
                    query.append(
                        {
                            "has_child": {
                                'type': CommentMappingType.get_mapping_type_name(),
                                "query": {
                                    "filtered": {
                                        "query": {"wildcard": search_data}
                                    }
                                }
                            }
                        }
                    )
                elif elastic_type == 'unit':
                    units_query.append({"wildcard": search_data})
                    query.append(
                        {
                            "has_child": {
                                'type': UnitMappingType.get_mapping_type_name(),
                                "query": {
                                    "filtered": {
                                        "query": {"wildcard": search_data}
                                    }
                                }
                            }
                        }
                    )
                elif elastic_type == 'experiment':
                    query.append(
                        {
                            "filtered": {
                                "query": {"wildcard": search_data}
                            }
                        }
                    )
                # elif elastic_type == 'measurement':
                #     measurement_query.append({"wildcard": search_data})
                #     query.append(
                #         {
                #             "has_child": {
                #                 'type': UnitMappingType.get_mapping_type_name(),
                #                 "query": {
                #                     "filtered": {
                #                         "query": {
                #                             "has_child": {
                #                                 'type': MeasurementMappingType.get_mapping_type_name(),
                #                                 "query": {
                #                                     "wildcard": search_data
                #                                 }
                #                             }
                #                         }
                #                     }
                #                 }
                #             }
                #         }
                #     )
                elif elastic_type == 'profile' or elastic_type == '_all':
                    profiles_query = ProfileMappingType.search()\
                        .query_raw({
                            "bool": {
                                "must":  {
                                    "filtered": {
                                        "query": {"wildcard": search_data}
                                    }
                                }
                            }
                        })
                    profiles = [user for user in profiles_query if User.objects.filter(pk=user['id']) and self.lab.is_assistant(User.objects.get(pk=user['id']))]

                if elastic_type == '_all':
                    comments_query.append({"match": search_data})
                    units_query.append({"match": search_data})
                    # measurement_query.append({"match": search_data})
                    query.extend([
                        {
                            "filtered": {
                                "filter": {
                                    'or': [
                                        {
                                            "query": {
                                                "query_string": {
                                                    "query": search_data.values()[0]
                                                }
                                            }
                                        },
                                        {
                                            "has_child": {
                                                'type': UnitMappingType.get_mapping_type_name(),
                                                "query": {
                                                    "filtered": {
                                                        "query": {"match": search_data}
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "has_child": {
                                                'type': CommentMappingType.get_mapping_type_name(),
                                                "query": {
                                                    "filtered": {
                                                        "query": {"match": search_data}
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                    ])

            experiments = ExperimentMappingType.search()\
                .filter_raw({'term': {'lab.id': self.kwargs['lab_pk']}})\
                .query_raw({
                    "bool": {
                        "must": query
                    }
                })

            # check permission
            if self.lab.is_guest(user):
                experiments = Experiment.objects.filter(Q(id__in=[experiment.id for experiment in experiments], active=True) &
                                                        (Q(owners=user) | Q(editors=user) | Q(viewers=user)))
            experiment_ids = {
                'has_parent': {
                    "parent_type": ExperimentMappingType.get_mapping_type_name(),
                    "query": {
                        "ids": {"values": [unicode(experiment.id) for experiment in experiments]}
                    }
                }
            }

            units_query.append(experiment_ids)
            units = UnitMappingType.search()\
                .query_raw({
                    "bool": {
                        "must": units_query
                    }
                })

            unit_ids = {
                'has_parent': {
                    "parent_type": UnitMappingType.get_mapping_type_name(),
                    "query": {
                        "ids": {"values": [unit.id for unit in units]}
                    }
                }
            }
            # measurement_query.append(unit_ids)
            # measurements = MeasurementMappingType.search()\
            #     .query_raw({
            #         "bool": {
            #             "must": measurement_query
            #         }
            #     })

            comments_query.append(experiment_ids)
            comments = CommentMappingType.search()\
                .query_raw({
                    "bool": {
                        "must": comments_query
                    }
                })
            return self.render_to_response(self.get_context_data(experiments=experiments, units=units, profiles=profiles,
                                                                 comments=comments))
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        ctx = kwargs.copy()
        ctx['form'] = self.form_class(self.request.GET)
        # ctx['create_collection_form'] = CollectionForm(initial={'lab': self.lab, 'user': self.request.user})
        ctx['update_experiment_form'] = UpdateUnitsForm(initial={'lab': self.lab, 'user': self.request.user})
        return ctx

