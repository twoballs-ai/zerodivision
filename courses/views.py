from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course


# Create your views here.
# Мы определим обработчики для создания, редактирования и удаления курсов,
# используя для этого не функции, а классы
# Это класс ManageCourseListView, который будет выступать в роли обработчика
# запросов. Он наследуется от класса ListView Django. Мы переопределили ме-
# тод get_queryset(), чтобы получать курсы, созданные текущим пользователем.
# Чтобы не дать пользователям возможности редактировать курсы, которые они
# не создавали, мы переопределим этот метод аналогичным образом в соответ-
# ствующих обработчиках.


# В этом фрагменте мы определили две примеси: OwnerMixin и OwnerEditMixin.
# Они будут добавлены к нашим обработчикам вместе с такими классами Django,
# как ListView, CreateView, UpdateView и DeleteView. Примесь OwnerMixin определяет
# метод get_queryset(). Он используется для получения базового QuerySetʼа, с ко-
# торым будет работать обработчик. Мы переопределили этот метод, так чтобы
# получать только объекты, владельцем которых является текущий пользователь
# (request.user).
class OwnerMixins(object):
    def get_queryset(self):
        qs = super(OwnerMixins, self).get_queryset()
        return qs.filter(owner= self.request.user)

class OwnerEditMixins(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixins, self).form_valid(form)



class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        qs = super(ManageCourseListView, self).get_queryset()
        return qs.filter(owner=self.request.user)
