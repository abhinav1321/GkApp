from django.urls import path

from .import views


urlpatterns = [
    path('', views.index, name='index'),
    path('exam', views.exam, name='exam'),
    path('get_topic', views.get_topic, name='get_topic'),
    path('practice', views.practice, name='practice'),
    path('add', views.add, name='add'),
    path('add_topic',views.add_topic,name='add_topic'),
    path('add_ques',views.add_ques,name='add_ques'),
    path('add_sub',views.add_sub,name='add_sub'),
    path('one_view',views.one_view,name='one_view'),
    path('count',views.count,name='count'),
    path('export_csv',views.export_csv,name='export_csv'),
    path('plot',views.plot,name='plot'),
    path('sessions',views.session_demo,name='sessions'),
    path('signIn', views.sign_in, name='signin'),
    path('hitview',views.hitview, name='hitview'),
    path('FormWizardView',views.FormWizardView,name='FormWizardView'),
    path('jquery_step',views.jquery_step, name='jquery_step'),
    path('new_ques_set',views.new_ques_set,name='new_ques_set'),
    path('full_test',views.full_test,name='full_test'),
    path('full_test_result_calculator',views.full_test_result_calculator,name='full_test_result_calculator'),
]
