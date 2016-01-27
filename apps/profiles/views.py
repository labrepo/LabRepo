from profiles.models import LabUser

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse_lazy, reverse
from django.template.loader import render_to_string
from django.views.generic import CreateView, UpdateView, DetailView
from django.utils.translation import ugettext_lazy as _

from common.mixins import LoginRequiredMixin, ActiveTabMixin, AjaxableResponseMixin
from labs.models import Lab
from .models import TempPassword
from .forms import InviteUserForm, UserUpdateForm


class InviteTechnician(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
    """
    View for inviting users and send mail to him
    """
    model = LabUser
    template_name = 'profiles/profile_form.html'
    form_class = InviteUserForm
    success_url = reverse_lazy('labs:list')

    def form_valid(self, form):
        self.object = form.save()
        context = {
            'site': settings.DOMAIN,  # todo change
            'user': self.object,
            'password': TempPassword.objects.get(user=self.object).password,
            'protocol': 'http',
        }
        subject = _('Invite')
        message = render_to_string('registration/invite_email.html', context)
        msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [self.object.email])
        msg.content_subtype = 'html'
        msg.send()
        return self.render_data()


class ProfileFormView(LoginRequiredMixin, ActiveTabMixin, UpdateView):
    """
    View for update a user's profile
    """
    model = LabUser
    template_name = 'profiles/profile_update.html'
    form_class = UserUpdateForm
    active_tab = 'profiles'

    def get_success_url(self):
        return reverse('profiles:detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        ctx = super(ProfileFormView, self).get_context_data(**kwargs)
        ctx['test_lab'] = bool(Lab.objects.filter(is_test=True) and self.object == self.request.user)
        return ctx


class ProfileDetailView(LoginRequiredMixin, ActiveTabMixin, DetailView):
    """
    View for detail a user's profile
    """
    model = LabUser
    template_name = 'profiles/profile_update.html'
    active_tab = 'profiles'
