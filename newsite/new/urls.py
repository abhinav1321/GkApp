from django.urls import path

from .import views


urlpatterns = [
    path('', views.index, name='index'),
    path('exam', views.exam, name='exam'),
    path('add', views.add, name='add'),
    path('add_topic',views.add_topic,name='add_topic'),
    path('add_ques',views.add_ques,name='add_ques'),
    path('add_sub',views.add_sub,name='add_sub'),
    path('one_view',views.one_view,name='one_view'),
    path('count',views.count,name='count'),
    path('export_csv',views.export_csv,name='export_csv'),
    path('plot',views.plot,name='plot'),
    path('sessions',views.session_demo,name='sessions'),
    path('signIn',views.signIn,name='signin'),
]
