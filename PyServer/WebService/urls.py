from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^train/backpropagation$', views.backPropagation_view),
]