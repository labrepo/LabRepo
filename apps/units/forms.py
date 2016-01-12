# -*- coding: utf-8 -*-
from common.forms import BaseForm

from .models import Unit


class UnitForm(BaseForm):
    def __init__(self, *args, **kwargs):
        kwargs.pop('lab_pk')
        super(UnitForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Unit
        exclude = ('lab', 'active')