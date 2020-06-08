from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.home),
    path('login/',views.login),
    path('login/logic/',views.loginLogic),
    path('register/',views.register),
    path('register/logic/',views.registerlogic),
    path('plagiarism/',views.postUpload),
    path('addfile/',views.addFile),
]
