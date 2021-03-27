from django.urls import path

from .import views

incorrect_username = "Incorrect username password"
int_ser_err = "Some Internal Server Error occurred"


handler404 = views.error_404
handler500 = views.error_500

urlpatterns = [
    path('', views.index, name='index'),
    path('error', views.ErrorView.as_view(), name='error'),

    path('internal_server_error',
         views.ErrorView.as_view(error_name=int_ser_err), name='error'),

    path('incorrect_username_error',
         views.ErrorView.as_view(error_name=incorrect_username), name='incorrect_username_error'),

    path('exam', views.exam, name='exam'),
    path('get_topic', views.get_topic, name='get_topic'),
    path('practice', views.practice, name='practice'),
    path('add', views.add, name='add'),
    path('add_topic', views.add_topic, name='add_topic'),
    path('add_ques', views.add_ques, name='add_ques'),
    path('add_sub', views.add_sub, name='add_sub'),
    path('test_result', views.test_result, name='test_result'),
    path('export_csv', views.export_csv, name='export_csv'),
    path('plot', views.plot, name='plot'),
    path('signIn', views.sign_in, name='signin'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('jquery_step', views.jquery_step, name='jquery_step'),
    path('full_test', views.full_test, name='full_test'),
    path('full_test_result_calculator', views.full_test_result_calculator, name='full_test_result_calculator'),
    path('user_analysis', views.user_analysis, name='user_analysis'),
    path('user_analysis_new', views.user_analysis_new, name='user_analysis'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('verify', views.verify, name='verify'),
    path('login_view', views.login_view, name='login_view'),
    path('login_process', views.login_process, name='login_process'),
    path('overall_details_analysis', views.get_overall_details_for_user_analysis, name='overall_details_analysis'),
    path('subject_list_user_analysis', views.get_subjects_for_user_analysis, name='subject_list_user_analysis'),
    path('subject_details_user_analysis', views.get_subject_details_for_user_analysis, name='subject_details_user_analysis'),
    path('topic_details_user_analysis', views.get_topics_details_for_user_analysis, name='topic_details_user_analysis'),
]
