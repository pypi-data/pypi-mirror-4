# -*- coding: utf-8 -*-

from django.db import models
from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError
import re

def validate_cpf(value):
    """
    CPF validation for Django fields.
    """
    # TODO: Internationalize.
    default_error_messages = {
        'invalid_cpf': u"Número de CPF inválido.",
        'max_digits_cpf': u"O CPF deve conter 11 dígitos.",
        'digits_only': u"Digíte apenas os números.",
    }
    
    def checksum(v):
        if v >= 2:
            return 11 - v
        return 0
    
    if value in EMPTY_VALUES:
        return u""

    if not value.isdigit():
        value = re.sub('[-\.]', '', value)
    orig_value = value[:]

    try:
        int(value)
    except ValueError:
        raise ValidationError(default_error_messages['digits_only'])

    if len(value) != 11:
        raise ValidationError(default_error_messages['max_digits_cpf'])
    orig_dv = value[-2:]

    new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(range(10, 1, -1))])
    new_1dv = checksum(new_1dv % 11)
    value = value[:-2] + str(new_1dv) + value[-1]
    new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(range(11, 1, -1))])
    new_2dv = checksum(new_2dv % 11)
    value = value[:-1] + str(new_2dv)
    if value[-2:] != orig_dv:
        raise ValidationError(default_error_messages['invalid_cpf'])

    return orig_value
    
class CPFField(models.CharField):
    """
    CPF validation field.
    Extends a CharField with brazilian CPF length and validation

    More information:
    http://en.wikipedia.org/wiki/Cadastro_de_Pessoas_F%C3%ADsicas
    """

    description = u"Extends a CharField with brazilian CPF length and validation"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 15
        kwargs['validators'] = [validate_cpf]
        super(CPFField, self).__init__(*args, **kwargs)

