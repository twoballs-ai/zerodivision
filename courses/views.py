from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


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
class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    succes_url = reverse_lazy('courses:manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    fileds = ['subject', 'title', 'slug', 'overview']
    succes_url = reverse_lazy('courses:manage_course_list')
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        qs = super(ManageCourseListView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class CourseCreateView(PermissionRequiredMixin,
                       OwnerCourseEditMixin,
                       CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateView(PermissionRequiredMixin,
                       OwnerCourseEditMixin,
                       UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(PermissionRequiredMixin,
                       OwnerCourseMixin,
                       DeleteView):
    template_name = 'courses/manage/course/delete.html'
    succes_url = reverse_lazy('manage_course_list')
    permission_required = 'courses.delete_course'

'''Примесь OwnerEditMixin определяет метод form_valid(). Django вызывает его
для обработчиков, которые наследуются от ModelFormMixin и работают с форма-
ми и модельными формами, например CreateView или UpdateView. Методы вы-
полняются, когда форма успешно проходит валидацию. Поведение по умолча-
нию для примеси Django – сохранение объекта в базу данных (для модельных
форм) и перенаправление пользователя на страницу по адресу success_url (для
обычных форм). Мы переопределили этот метод, чтобы автоматически запол-
нять поле owner сохраняемого объекта.
Примесь OwnerMixin можно применять для любого обработчика, который ра-
ботает с моделью, содержащей поле owner.
Мы также создали класс OwnerCourseMixin, который наследуется от OwnerMixin,
и добавили для него атрибут model – модель, с которой работает обработчик'''
