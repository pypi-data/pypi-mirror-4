from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.GoalList.as_view(), name='reward_goals'),
    url(r'^create/$', views.CreateGoal.as_view(), name='reward_create_goal'),
    url(r'^delete/(?P<pk>\d+)/$', views.DeleteGoal.as_view(), name='reward_delete_goal'),
    url(r'^manage/$', views.ManageGoal.as_view(), name='reward_manage_goal'),
    url(r'^achievements/$', views.AchievementList.as_view(), name='reward_achievements'),
    url(r'^(?P<pk>\d+)/increment/$', views.IncrementScore.as_view(), name='reward_increment_score'),
    url(r'^(?P<pk>\d+)/decrement/$', views.DecrementScore.as_view(), name='reward_decrement_score'),
    url(r'^(?P<pk>\d+)/achieved/$', views.Achieved.as_view(), name='reward_achieved'),
)
