# -*- coding: utf8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


home_view = login_required(TemplateView.as_view(template_name = "account/home.html"))
login_view = TemplateView.as_view(template_name='account/login-form.html')
