from django import forms

from crispy_forms.helpers import FormHelper, Fieldset, Field, Layout, Submit
from crispy_forms.bootstrap import FormActions

from . import models


class AchievementForm(forms.ModelForm):
    name = forms.CharField(label='Goal name')
    target = forms.IntegerField(min_value=models.TARGET_MIN, max_value=models.TARGET_MAX,
        label='How many stars to achieve the goal?')
    next_url = forms.CharField(required=False, max_length=255, widget=forms.HiddenInput)

    class Meta:
        model = models.Achievement
        fields = ['name', 'target']

    helper = FormHelper()
    helper.form_tag = True
    helper.form_action = 'reward_create_goal'
    helper.form_class = 'add-goal-form'
    helper.layout = Layout(
        Fieldset(
            '',
            Field('name', placeholder='Set a new goal for your child'),
            Field('target', placeholder='00', maxlength='2')
        ),
        FormActions(
            Submit('submit', 'Create', css_class='button')
        )
    )


class AchievementDeleteForm(forms.Form):
    helper = FormHelper()
    helper.form_tag = False
    helper.layout = Layout(
        FormActions(
            Submit('submit', 'Delete', css_class='button button-important')
        )
    )
