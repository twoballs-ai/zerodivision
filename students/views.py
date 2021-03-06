from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from courses.models import Course
from .forms import CourseEnrollForm



class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super(StudentEnrollCourseView,
                     self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('students:student_course_detail',
                            args=[self.course.id])


# страницу, показывающую студентам курсы, в ко-
# торых они уже принимают участие, и страницу содержимого курса
class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super(StudentCourseListView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])


# Это обработчик StudentCourseDetailView. Мы переопределили метод get_queryset(),
# чтобы ограничить QuerySet курсов и работать только с теми, на которые
# записан текущий пользователь. Мы также переопределили метод get_context_
# data(), чтобы добавить в контекст шаблона данные о модуле, если его иден-
# тификатор был передан в параметре module_id URLʼа. В противном случае мы
# показываем содержимое первого модуля. Так студенты смогут переходить от
# одного модуля курса к другому.
class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super(StudentCourseDetailView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super(StudentCourseDetailView,
                        self).get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(
                                    id=self.kwargs['module_id'])
        else:
            # get first module
            context['module'] = course.modules.all()[0]
        return context
