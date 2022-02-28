from django.shortcuts import render
from django.views.generic.list import ListView
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
class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        qs = super(ManageCourseListView, self).get_queryset()
        return qs.filter(owner = self.request.user)