"""
authentication/views.py

Created on Oct. 23, 2017
by Jiayao
"""
from __future__ import (absolute_import)
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from account.models import (User, Tutor, Student, SubjectTag,
                           Course)
from .forms import (UserForm, TutorForm)


class IndexView(generic.TemplateView):
    """Models the index view."""
    template_name = 'signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['choice'] = True
        context['user_form'] = None
        context['student_form'] = None
        context['tutor'] = None
        return context


class StudentFormView(generic.edit.CreateView):
    """Models the sign-up form."""
    template_name = 'signup.html'
    form_class = UserForm

class UserFormView(generic.edit.CreateView):
    """Models the sign-up form."""
    template_name = 'signup.html'
    form_class = UserForm

class TutorFormView(generic.edit.CreateView):
    """Models the sign-up form."""
    template_name = 'signup.html'
    form_class = TutorForm


class StudentView(generic.TemplateView):
    template_name = 'signup.html'

    def get(self, req, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['choice'] = False
        context['user_form'] = None
        context['student_form'] = UserForm()
        context['tutor_form'] = None
        return self.render_to_response(context)


class TutorView(generic.TemplateView):
    template_name = 'signup.html'

    def get(self, req, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['choice'] = False
        context['user_form'] = UserForm()
        context['student_form'] = None
        context['tutor_form'] = TutorForm()
        return self.render_to_response(context)



class BothView(generic.TemplateView):
    """Models the sign-up form."""
    template_name = 'signup.html'

    def get(self, req, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['choice'] = False
        context['user_form'] = None
        context['student_form'] = UserForm()
        context['tutor_form'] = TutorForm()
        return self.render_to_response(context)

