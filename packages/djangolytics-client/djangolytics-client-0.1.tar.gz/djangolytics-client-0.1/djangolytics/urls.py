from django.conf.urls.defaults import patterns, url

from djangolytics import views

urlpatterns = patterns("",

    url(
        regex=r"^$",
        view=views.DjangolyticsView.as_view(),
        name="djangolytics_modified",
    ),

)