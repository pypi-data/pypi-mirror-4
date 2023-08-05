import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import F
from django.http import HttpResponseRedirect, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View, DetailView
from django.views.generic.edit import CreateView, DeleteView

from .forms import AchievementForm, AchievementDeleteForm
from .models import Achievement


class JSONResponse(HttpResponse):
    def __init__(self, *args, **kwargs):
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(*args, **kwargs)


def class_view_decorator(function_decorator):
    def simple_decorator(View):
        View.dispatch = method_decorator(function_decorator)(View.dispatch)
        return View
    return simple_decorator


@class_view_decorator(login_required)
class GoalList(ListView):
    template_name = 'rewards/goal_list.html'

    def get_queryset(self):
        profile = self.request.user.profile
        return Achievement.objects.incomplete_for_profile(profile)

    def render_to_response(self, context, **response_kwargs):
        if not self.get_queryset():
            context.update({
                'form': AchievementForm
            })

        return super(GoalList, self).render_to_response(context, **response_kwargs)


@class_view_decorator(login_required)
class AchievementList(ListView):
    template_name = 'rewards/achievement_list.html'

    def get_queryset(self):
        profile = self.request.user.profile
        return Achievement.objects.complete_for_profile(profile).filter(score=F('target'))


@class_view_decorator(login_required)
class ManageGoal(ListView):
    template_name = 'rewards/manage_goal_list.html'

    def get_queryset(self):
        profile = self.request.user.profile
        qs = Achievement.objects.incomplete_for_profile(profile)
        return qs

    def get_context_data(self, **kwargs):
        next_url = reverse('reward_manage_goal')

        profile = self.request.user.profile
        achievement_list = Achievement.objects.complete_for_profile(profile)

        context = super(ManageGoal, self).get_context_data(**kwargs)
        context.update({
            'form': AchievementForm(initial={'next_url': next_url}),
            'delete_form': AchievementDeleteForm,
            'achievement_list': achievement_list,
        })

        return context


@class_view_decorator(login_required)
class CreateGoal(CreateView):
    form_class = AchievementForm
    model = Achievement
    success_url = reverse_lazy('reward_goals')

    def get_form(self, form_class):
        form = super(CreateGoal, self).get_form(form_class)
        form.instance.profile = self.request.user.profile

        return form

    def form_valid(self, form):
        if form.cleaned_data['next_url']:
            self.success_url = form.cleaned_data['next_url']

        return super(CreateGoal, self).form_valid(form)


@class_view_decorator(login_required)
class DeleteGoal(DeleteView):
    model = Achievement
    success_url = reverse_lazy('reward_manage_goal')

    def get_object(self):
        obj = super(DeleteGoal, self).get_object()
        if not obj.profile == self.request.user.profile:
            raise Http404
        return obj


class ModifyScoreView(View):
    def post(self, request, *args, **kwargs):
        self.obj = self.get_object()
        self.modify_object(self.obj)
        return self.get_response()

    def get_object(self):
        pk = self.kwargs['pk']
        profile = self.request.user.profile
        obj = get_object_or_404(Achievement, pk=pk, profile=profile)
        return obj

    def get_response(self):
        if self.request.is_ajax():
            return JSONResponse(json.dumps({'score': self.obj.score}))
        return HttpResponseRedirect(reverse('reward_goals'))


@class_view_decorator(login_required)
class Achieved(DetailView):
    template_name = 'rewards/achieved.html'
    model = Achievement

    def get_object(self):
        pk = self.kwargs['pk']
        profile = self.request.user.profile
        qs = Achievement.objects.filter(profile=profile, score=F('target'))
        return get_object_or_404(qs, pk=pk)


@class_view_decorator(login_required)
class IncrementScore(ModifyScoreView):
    def modify_object(self, obj):
        obj.increment_score()

    def get_response(self):
        if self.obj.achieved():
            if self.request.is_ajax():
                # Ajax & finished: send back body of achievement view.
                pk = self.obj.pk
                template = 'rewards/_achieved_body.html'
                req = HttpRequest()
                req.user = self.request.user
                req.method = 'GET'
                return Achieved(template_name=template).dispatch(req, pk=pk)

            # Finished: redirect to achievement view.
            return HttpResponseRedirect(reverse('reward_achieved', kwargs={'pk': self.kwargs['pk']}))

        # Continue as per super-class.
        return super(IncrementScore, self).get_response()


@class_view_decorator(login_required)
class DecrementScore(ModifyScoreView):
    def modify_object(self, obj):
        obj.decrement_score()
