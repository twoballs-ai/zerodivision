from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content


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
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    fileds = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('courses:manage_course_list')
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
    success_url = reverse_lazy('courses:manage_course_list')
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


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('courses:manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super(ContentCreateUpdateView,
                     self).dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # Создаем новый объект.
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect('module_content_list', self.module.id)

        return self.render_to_response({'form': form,
                                        'object': self.obj})


class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)

        return self.render_to_response({'module': module})