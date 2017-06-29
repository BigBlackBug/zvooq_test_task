from django.conf.urls import url

from service.views import MainView

app_name = 'service'
urlpatterns = [
    url(r'^from_cache', MainView.as_view(), name='main'),
]
