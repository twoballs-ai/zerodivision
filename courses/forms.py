from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module

# Мы также передали в фабричную функцию следующие аргументы:
# fields – поля, которые будут добавлены для каждой формы набора;
# extra – количество дополнительных пустых форм модулей;
# can_delete. Если установить его в True, Django добавит для каждой формы
ModuleFormSet = inlineformset_factory(Course,
                                      Module,
                                      fields=['title', 'description'],
                                      extra=2,
                                      can_delete=True)
