"""
URL configuration for format_specifications project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.upload_word_page, name='upload_word_page'),
    path('ai_format/', views.ai_format_word, name='ai_format_word'),
    path('api/template-details/<str:template_id>/', views.api_template_details, name='api_template_details'),
    path('api/processing-status/', views.ai_processing_status, name='ai_processing_status'),
    path('processing-status/', views.processing_status, name='processing_status'),
    path('template/', views.template_generation_page, name='template_generation_page'),
    path('template/generate/', views.generate_from_template, name='generate_from_template'),
    path('segment/', views.segmentation_only_page, name='segmentation_only_page'),
    path('segment/segment-document/', views.segment_document, name='segment_document'),
]