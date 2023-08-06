from django.conf import settings
from django.db import models
from django.contrib.auth.models import UserManager, User
from django.utils.translation import ugettext_lazy as _
from webutils.djtools.email import send_simple_email


class BaseUserProfileManager(UserManager):
    def generate_hash(self):
        import hashlib
        import random

        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        random_string = User.objects.make_random_password()
        return hashlib.sha1(salt + random_string).hexdigest()

    def send_user_email(self, user, subject, context, template):
        send_simple_email(
            user.email,
            subject,
            context,
            template,
            is_template_file=True,
        )

    def add_new_user(self, username, password, email, first_name, last_name):
        new_user = User.objects.create_user(username, email, password)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.is_active = True
        new_user.save()

        # User Profile
        return self.create(user=new_user)

    def reset_user_password(self, key):
        import re

        if re.match('^[a-f0-9]{40}$', key):
            try:
                profile = self.get(activation_key=key)
            except self.model.DoesNotExist:
                return False

            user = profile.user
            new_password = User.objects.make_random_password(length=8)
            user.set_password(new_password)
            user.save()

            profile.activation_key = ''
            profile.save()

            subject = 'Your Password Reset Request'
            ctext = {
                'password': new_password,
            }
            self.send_user_email(
                user,
                subject,
                ctext,
                'baseacct/reset_email_done.txt'
            )
            return user
        return False


class BaseUserProfile(models.Model):
    user = models.ForeignKey(
        User,
        unique=True,
        verbose_name=_('User Account'),
        help_text=_('User Profiles must be "tied" to a user account.'),
        related_name='%(app_label)s_%(class)s_set',
    )
    
    # Activation Key
    activation_key = models.CharField(
        max_length=125,
        blank=True,
        editable=False,
    )

    # Custom Manager
    objects = BaseUserProfileManager()

    # Metadata
    class Meta:
        abstract = True
        ordering = ('user',)

    # Functions
    def __unicode__(self):
        return u'%s' % (self.user.username)
