from django.db import models
from django.core.urlresolvers import reverse


TARGET_MIN = 3
TARGET_MAX = 20


class Badge(models.Model):
    name = models.CharField(max_length=127, unique=True)
    image = models.ImageField(upload_to='badges')
    min_target = models.PositiveSmallIntegerField(default=TARGET_MIN)

    def __unicode__(self):
        return self.name


class AchievementManager(models.Manager):
    def complete(self):
        """Get Achievements where score == target."""
        return self.get_query_set().filter(score=models.F('target'))

    def incomplete(self):
        """Get Achievements where score != target."""
        return self.get_query_set().exclude(score=models.F('target'))

    def complete_for_profile(self, profile):
        return self.complete().filter(profile=profile)

    def incomplete_for_profile(self, profile):
        return self.incomplete().filter(profile=profile)


class Achievement(models.Model):
    profile = models.ForeignKey('profiles.Profile')
    name = models.CharField(max_length=127)
    target = models.PositiveSmallIntegerField()
    score = models.PositiveSmallIntegerField(default=0)
    badge = models.ForeignKey(Badge, null=True, blank=True)

    objects = AchievementManager()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Sanity check self.target
        if self.target is None:
            self.target = TARGET_MIN
        if self.target <= TARGET_MIN:
            self.target = TARGET_MIN
        if self.target > TARGET_MAX:
            self.target = TARGET_MAX

        # Sanity check self.score
        if self.score is None or self.score < 0:
            self.score = 0
        if self.score > self.target:
            self.score = self.target

        # Assign badges to completed goals.
        if self.achieved() and not self.badge:
            self.assign_random_badge()
        return super(Achievement, self).save(*args, **kwargs)

    def get_increment_url(self):
        return reverse('reward_increment_score', kwargs={'pk': self.pk})

    def get_decrement_url(self):
        return reverse('reward_decrement_score', kwargs={'pk': self.pk})

    def achieved(self):
        """If an Achievement's score == target, then it must be complete."""
        return self.score == self.target
    achieved.boolean = True  # This enables the Boolean icons in the admin.

    def increment_score(self, commit=True):
        if not self.achieved():
            self.score = self.score + 1
        if commit:
            self.save()

    def decrement_score(self, commit=True):
        if not self.achieved():
            self.score = self.score - 1
        if commit:
            self.save()

    def assign_random_badge(self):
        """Associate this Achievement with a random badge."""
        try:
            badge = Badge.objects.filter(min_target__gte=self.target).order_by('?')[0]
        except IndexError:
            pass
        else:
            self.badge = badge
