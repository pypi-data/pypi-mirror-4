# -*- coding: utf-8 -*-

import django.db.models
import inoa.models.utils

setattr(django.db.models.Model, '__unicode__', inoa.models.utils.default_repr)
