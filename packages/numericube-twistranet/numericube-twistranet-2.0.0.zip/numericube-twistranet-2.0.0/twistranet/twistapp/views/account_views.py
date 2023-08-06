import hashlib
import urllib
import time

from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError
from django.forms import widgets
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib.auth.models import User, UNUSABLE_PASSWORD
from django.contrib.sites.models import RequestSite
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings
from twistranet.twistapp.signals import invite_user, reset_password

from twistranet.twistapp.models import *
from twistranet.twistapp.forms import account_forms, registration_forms
from twistranet.twistapp.lib.slugify import slugify
from twistranet.actions import *
from twistranet.core.views import *

class UserAccountView(BaseWallView):
    """
    This is what is used as a base view for accounts
    """
    context_boxes = [
        'account/profile.box.html',
        'actions/context.box.html',
        'account/relations.box.html',
    ]

    template_variables = BaseWallView.template_variables + [
        "account",
        "n_communities",
        "n_network_members"
    ]

    model_lookup = UserAccount
    template = "account/view.html"
    title = None
    name = "account_by_id"

    def prepare_view(self, *args, **kw):
        """
        Add a few parameters for the view
        """
        # Regular creation
        super(UserAccountView, self).prepare_view(*args, **kw)
        if not hasattr(self, "useraccount"):
            self.useraccount = self.auth
        self.account = self.useraccount
        self.n_communities = self.account and self.account.communities.count() or False
        self.n_network_members = self.account and self.account.network.count() or False
        
        # Add a message for ppl who have no content
        if self.template == UserAccountView.template:
            if self.account and self.auth and self.account.id == self.auth.id:
                if not Content.objects.filter(publisher = self.auth).exists():
                    messages.info(self.request, mark_safe(_("""<p>
                        It seems that you do not have created content yet. Maybe it's time to do so!
                        </p>
                        <p>
                        Creating content in twistranet is easy. For example, just tell what you're working on in the form below and click the "Send" button.
                        </p>
                        <p>
                        Want to learn about what you can do in twistranet? Just take a look here: [help]
                        </p>
                    """)))

    def get_objects_list(self,):
        return Content.objects.getActivityFeed(self.object)

    def get_recent_content_list(self):
        """
        Retrieve recent content list for the given account.
        XXX TODO: Optimize this by adding a (first_twistable_on_home, last_twistable_on_home) values pair on the Account object.
        This way we can just query objects with id > last_twistable_on_home
        """
        nb_all = self.objects_list.count()
        batch = self.batch_list(nb_all)
        nb_from = batch[0]
        nb_to = batch[1]
        if nb_from < nb_all:
            objects_list = self.objects_list.order_by("-id").values_list('id', flat = True)[nb_from:nb_to]
            latest_list = Content.objects.__booster__.filter(id__in = tuple(objects_list)).select_related(*self.select_related_summary_fields).order_by("-created_at")
            return latest_list
        return []

    def get_title(self,):
        """
        We override get_title in a way that it could be removed easily in subclasses.
        Just define a valid value for self.title and this get_title() will keep the BaseView behaviour
        """
        if not self.title:
            return _("%(name)s's profile") % {'name': self.account.title}
        return super(UserAccountView, self).get_title()

class HomepageView(UserAccountView):
    """
    Special treatment for homepage.
    """
    name = "twistranet_home"
    title = _("Timeline")
        
    def get_objects_list(self):
        """
        Retrieve recent content list for the given account.
        XXX TODO: Optimize this by adding a (first_twistable_on_home, last_twistable_on_home) values pair on the Account object.
        This way we can just query objects with id > last_twistable_on_home
        """
        objects_list = None
        if not self.auth.is_anonymous:
            if Content.objects.filter(publisher = self.auth).exists():
                objects_list = Content.objects.followed.exclude(model_name = "Comment")
        if objects_list is None:
            objects_list = Content.objects.exclude(model_name = "Comment")
        return objects_list
    
    def prepare_view(self, ):
        """
        We just have the account set as curently-auth account.
        """
        # Get the actual view instance. Not optimal, but, well, works.
        if not self.auth.is_anonymous:
            prep_id = self.auth.id
        else:
            prep_id = None
        super(HomepageView, self).prepare_view(prep_id)


class PublicTimelineView(UserAccountView):
    name = "timeline"
    title = _("Public timeline")
    
    def get_objects_list(self):
        """
        Just return all public / available content
        """
        return Content.objects.exclude(model_name = "Comment")


#                                                                               #
#                               LISTING VIEWS                                   #
#                                                                               #

class AccountListingView(BaseView):
    """
    Todo: ALL accounts listing page.
    """
    title = _("Accounts")
    template = "account/list.html"
    template_variables = BaseView.template_variables + [
        "accounts",
    ]

    def prepare_view(self, ):
        super(AccountListingView, self).prepare_view()
        self.accounts = Account.objects.get_query_set()[:settings.TWISTRANET_COMMUNITIES_PER_PAGE]
        
        
class AccountNetworkView(AccountListingView, UserAccountView):
    """
    All networked accounts for an account page
    """
    template = AccountListingView.template
    template_variables = UserAccountView.template_variables + AccountListingView.template_variables

    def get_title(self,):
        if self.account.id == self.auth.id:
            return _("Your network")
        return _("%(name)s's network" % {'name': self.account.title} )

    def prepare_view(self, *args, **kw):
        super(AccountNetworkView, self).prepare_view()
        UserAccountView.prepare_view(self, *args, **kw)
        self.accounts = self.account.network   


class AccountCommunitiesView(AccountListingView, UserAccountView):
    """
    All communities for an account.
    """
    template = AccountListingView.template
    template_variables = UserAccountView.template_variables + AccountListingView.template_variables

    def get_title(self,):
        if self.account.id == self.auth.id:
            return _("Your communities")
        return _("%(name)s's communities" % {'name': self.account.title} )

    def prepare_view(self, *args, **kw):
        super(AccountCommunitiesView, self).prepare_view()
        UserAccountView.prepare_view(self, *args, **kw)
        self.accounts = self.account.communities    


class AccountAdminCommunitiesView(AccountListingView, UserAccountView):
    """
    All communities administred by an account.
    """
    template = AccountListingView.template
    template_variables = UserAccountView.template_variables + AccountListingView.template_variables

    # XXX TODO
    
    def get_title(self,):
        if self.account.id == self.auth.id:
            return _("Your communities")
        return _("%(name)s's communities" % {'name': self.account.title} )

    def prepare_view(self, *args, **kw):
        super(AccountCommunitiesView, self).prepare_view(*args, **kw)
        UserAccountView.prepare_view(self, *args, **kw)
        self.accounts = self.account.communities


class PendingNetworkView(AccountListingView, UserAccountView):
    """
    All pending network relations for an account
    """
    template = AccountListingView.template
    template_variables = UserAccountView.template_variables + AccountListingView.template_variables
    title = _("Pending network requests")
    name = "account_pending_network"
    category = ACCOUNT_ACTIONS
    
    def as_action(self,):
        """Only return the action if there's pending nwk requests
        """
        if self.auth.is_anonymous:
            return
        req = self.auth.get_pending_network_requests()
        if not req:
            return
        action = BaseView.as_action(self)
        action.label = mark_safe(_('<span class="badge">%(number)d</span> Pending network requests') % {"number": len(req)})
        return action
            
    def prepare_view(self, *args, **kw):
        super(PendingNetworkView, self).prepare_view()
        UserAccountView.prepare_view(self, self.auth.id)
        self.accounts = self.account.get_pending_network_requests()


#                                                                               #
#                                   ACTION VIEWS                                #
#                                                                               #

class AccountDelete(BaseObjectActionView):
    """
    Delete a community from the base
    """
    model_lookup = UserAccount
    name = "account_delete"
    confirm = _("Do you really want to delete this account?<br />All content for this user WILL BE DELETED.")
    title = _("Delete account")
 
    def as_action(self):
        if not isinstance(getattr(self, "object", None), self.model_lookup):
            return None
        if not self.object.can_delete:
            return None
        # Can't delete myself ;)
        if self.object.id == Twistable.objects.getCurrentAccount(self.request).id:
            return None
        return super(AccountDelete, self).as_action()

    def prepare_view(self, *args, **kw):
        super(AccountDelete, self).prepare_view(*args, **kw)
        if not self.object.can_delete:
            raise ValueError("You're not allowed to delete this account")
        name = self.useraccount.title
        underlying_user = self.useraccount.user
        __account__ = SystemAccount.get()
        # self.useraccount.delete()
        underlying_user.delete()
        del __account__
        messages.info(
            self.request, 
            _("'%(name)s' account has been deleted.") % {'name': name},
        )
        raise MustRedirect(reverse("twistranet_home"))
    

class AddToNetworkView(BaseObjectActionView):
    """
    Add sbdy to my network, with or without authorization
    """
    model_lookup = UserAccount
    name = "add_to_my_network"
    
    def as_action(self, ):
        """
        as_action(self, ) => generate the proper action.
        """
        if not hasattr(self, "object"):
            return None
        if not isinstance(self.object, UserAccount):
            return None
        
        # Networking actions
        if self.object.has_pending_network_request:
            return Action(
                label = _("Accept in your network"),
                url = reverse(self.name, args = (self.object.id, ), ),
                confirm = _(
                    "Would you like to accept %(name)s in your network?<br />"
                    "He/She will be able to see your network-only content."
                    ) % { "name": self.object.title },
                category = MAIN_ACTION,
            )
                            
        elif self.object.can_add_to_my_network:
            return Action(
                label = _("Add to your network"),
                url = reverse(self.name, args = (self.object.id, ), ),
                confirm = _(
                    "Would you like to add %(name)s to your network?<br />"
                    "He/She will have to agree to your request."
                    ) % {"name": self.object.title},
                category = MAIN_ACTION,
            )
    
    def prepare_view(self, *args, **kw):
        super(AddToNetworkView, self).prepare_view(*args, **kw)
        self.redirect = self.useraccount.get_absolute_url()
        self.useraccount.add_to_my_network()
        name = self.useraccount.title
        if self.useraccount in self.auth.network:
            messages.success(
                self.request, 
                _("You're now connected with %(name)s.") % {'name': name}
            )
        else:
            messages.info(
                self.request, 
                _("A network request has been sent to %(name)s for approval.") % {'name': name}
            )
        

class RemoveFromNetworkView(BaseObjectActionView):
    """
    Add sbdy to my network, with or without authorization
    """
    model_lookup = UserAccount
    name = "remove_from_my_network"

    def as_action(self, ):
        if not isinstance(getattr(self, "object", None), self.model_lookup):
            return None
        if self.object.has_received_network_request:
            return Action(
                category = LOCAL_ACTIONS,
                label = _("Cancel your network request"),
                url = reverse(self.name, args = (self.object.id, ), ),
                confirm = _("Would you like to cancel your network request?"),
            )
        if self.object.in_my_network:
            return Action(
                category = LOCAL_ACTIONS,
                label = _("Remove from your network"),
                url = reverse(self.name, args = (self.object.id, ), ),
                confirm = _("Would you like to remove %(name)s from your network?") % {"name": self.object.title},
            )

    def prepare_view(self, *args, **kw):
        super(RemoveFromNetworkView, self).prepare_view(*args, **kw)
        self.redirect = self.useraccount.get_absolute_url()
        was_in_my_network = self.useraccount in self.auth.network
        self.useraccount.remove_from_my_network()
        name = self.useraccount.title
        if was_in_my_network:
            messages.success(
                self.request, 
                _("You're not connected with %(name)s anymore.") % {'name': name}
            )
        else:
            messages.info(
                self.request, 
                _("Your network request to %(name)s has been canceled.") % {'name': name}
            )


#                                                                           #
#                           Edition / Creation views                        #
#                                                                           #

class UserAccountEdit(UserAccountView):
    """
    Edit form for user account. Not so far from the view itself.
    """
    template = "account/edit.html"
    form_class = account_forms.UserAccountForm
    content_forms = []
    latest_content_list = []
    name = "user_account_edit"
    category = LOCAL_ACTIONS
    
    def as_action(self,):
        """
        Return action only if can_edit user
        """
        if not self.is_model:
            return None
        if self.object.can_edit:
            return super(UserAccountEdit, self).as_action()
    
    def get_title(self,):
        """
        Title suitable for creation or edition
        """
        if self.title:
            return super(UserAccountEdit, self).get_title()
        if not getattr(self, 'object', None):
            return _("Create a user account")
        elif self.object.id == self.auth.id:
            return _("Edit your account")
        return _("Edit %(name)s" % {'name' : self.object.title })

class UserAccountInvite(UserAccountEdit):
    """
    UserAccount invitation. Close to the edit class!
    """
    context_boxes = []
    form_class = account_forms.UserInviteForm
    title = _("Invite user")
    category = GLOBAL_ACTIONS
    name = "user_account_invite"
    
    def as_action(self):
        if not Account.objects.can_create:
            return None
        return BaseView.as_action(self)
        
    def prepare_view(self):
        """
        Process additional form stuff.
        Here we've got a valid self.form object.
        """
        super(UserAccountInvite, self).prepare_view()
        is_admin = UserAccount.objects.getCurrentAccount(self.request).is_admin
        if not is_admin:
            self.form.fields['make_admin'].widget = widgets.HiddenInput()
        if self.form_is_valid:
            # Double-check that user is not already registered
            email = self.form.cleaned_data['email']
            if User.objects.filter(email = email).exists():
                messages.error(self.request, _("This user already exists."))
                self.form_is_valid = False
            
        if self.form_is_valid:
            # Generate the invitation link.
            # Invitation is in two parts: the verification hash and the email address.
            admin_string = ""
            if is_admin:
                if self.form.cleaned_data['make_admin']:
                    admin_string = "?make_admin=1"
            h = "%s%s%s" % (settings.SECRET_KEY, email, admin_string)
            h = hashlib.md5(h).hexdigest()
            invite_link = reverse(AccountJoin.name, args = (h, urllib.quote_plus(email)))

            # Send the invitation (as a signal)
            invite_user.send(
                sender = self.__class__,
                inviter = UserAccount.objects.getCurrentAccount(self.request),
                invitation_uri = "%s" % (invite_link, ),
                target = email,
                message = self.form.cleaned_data['invite_message'],
            )
            
            # Say we're happy and redirect
            if self.form_is_valid:
                messages.success(self.request, _("Invitation sent successfuly."))
                raise MustRedirect(reverse(self.name))
    
#                                                                                           #
#                                   Account login/logout/join                               #
#                                                                                           #

class AccountJoin(UserAccountEdit):
    """
    join TN
    """
    template = "registration/join.html"
    form_class = account_forms.UserAccountCreationForm
    name = "account_join"
    title = _("Join")
    
    def prepare_view(self, check_hash, email):
        """
        Render the join form.
        """
        # Check if hash and email AND admin priviledge match
        is_admin = False
        admin_string = "?make_admin=1"
        h = "%s%s%s" % (settings.SECRET_KEY, email, admin_string)
        h = hashlib.md5(h).hexdigest()
        if check_hash == h:
            is_admin = True
        else:
            # Check if hash and email match.
            h = "%s%s" % (settings.SECRET_KEY, email)
            h = hashlib.md5(h).hexdigest()
            if not check_hash == h:
                raise ValidationError("Invalid email. This invitation has been manually edited.")
            
        # If user is already registered, return to login form
        if User.objects.filter(email = email).exists():
            raise MustRedirect(reverse(AccountLogin.name))
        
        # Call form processing. Prepare all arguments, esp. email and username
        username = email.split('@')[0]
        username = slugify(username)
        self.initial = {
            "email":    email,
            "username": username,
        }
        super(AccountJoin, self).prepare_view()
        
        # Now save user info. But before, double-check that stuff is still valid
        if self.form_is_valid:
            cleaned_data = self.form.cleaned_data
            # Check password and username
            if not cleaned_data["password"] == cleaned_data["password_confirm"]:
                messages.warning(self.request, _("Password and confirmation do not match"))
            elif User.objects.filter(username = cleaned_data["username"]).exists():
                messages.warning(self.request, _("A user with this name already exists."))
            else:
                # Create user and set information
                __account__ = SystemAccount.get()
                u = User.objects.create(
                    username = cleaned_data["username"],
                    first_name = cleaned_data["first_name"],
                    last_name = cleaned_data["last_name"],
                    email = cleaned_data["email"],
                    is_superuser = is_admin,
                    is_active = True,
                )
                u.set_password(cleaned_data["password"])
                u.save()
                useraccount = UserAccount.objects.get(user = u)
                useraccount.title = u"%s %s" % (cleaned_data["first_name"], cleaned_data["last_name"])
                useraccount.save()
                if is_admin:
                    admin_community = AdminCommunity.objects.get()
                    if not admin_community in useraccount.communities:
                        admin_community.join(useraccount, is_manager = True)
                del __account__
                
                # Display a nice success message and redirect to login page
                messages.success(self.request, _("Your account is now created. You can login to twistranet."))
                raise MustRedirect(reverse(AccountLogin.name))

class AccountLogin(BaseView):
    template = "registration/login.html"
    name = "login"
    title = _("Login")
    template_variables = BaseView.template_variables + \
        ['form', 'site', 'next', ]
    global_boxes = [
        'registration/introduction.box.html',
    ]
    
    def prepare_view(self,):
        """
        request, template_name='registration/login.html',
              redirect_field_name=REDIRECT_FIELD_NAME,
              authentication_form=AuthenticationForm):
        Displays the login form and handles the login action.
        this is from django.contrib.auth.views
        """
        from django.contrib.auth.views import REDIRECT_FIELD_NAME as redirect_field_name        # = 'next'
        from django.contrib.auth.views import AuthenticationForm as authentication_form
        from django.contrib.auth.views import auth_login
        from django.contrib.sites.models import Site, RequestSite
        redirect_to = self.request.REQUEST.get(redirect_field_name, '')

        if self.request.method == "POST":
            self.form = authentication_form(data=self.request.POST)
            if self.form.is_valid():
                # Light security check -- make sure redirect_to isn't garbage.
                if not redirect_to or ' ' in redirect_to:
                    redirect_to = settings.LOGIN_REDIRECT_URL

                # Heavier security check -- redirects to http://example.com should 
                # not be allowed, but things like /view/?param=http://example.com 
                # should be allowed. This regex checks if there is a '//' *before* a
                # question mark.
                elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL

                # Okay, security checks complete. Log the user in.
                auth_login(self.request, self.form.get_user())
                setattr(self, redirect_field_name, redirect_to)    
                if self.request.session.test_cookie_worked():
                    self.request.session.delete_test_cookie()
                raise MustRedirect(redirect_to)
            else:
                # Invalid user/password
                messages.warning(self.request, _("Sorry, that's not a valid username or password"))
        else:
            self.form = authentication_form(self.request)

        self.request.session.set_test_cookie()

        if Site._meta.installed:
            self.site = Site.objects.get_current()
        else:
            self.site = RequestSite(self.request)
        setattr(self, redirect_field_name, redirect_to)
    
    
class AccountForgottenPassword(AccountLogin):
    """
    Forgotten pwd. Sorry, this has yet to be implemented.
    """
    name = "forgotten_password"
    title = _("Forgot your password")
    template = "registration/forgotten.html"
    template_variables = BaseView.template_variables + ['form', ]
    
    def prepare_view(self,):
        if self.request.method == "POST":
            self.form = registration_forms.ForgottenPasswordForm(data=self.request.POST)
            if self.form.is_valid():
                # Generate the reset password link.
                # The link is in two parts: the verification hash and the email.
                # The verification hash is a combination of the server's secret key, user's email,
                # HASHED version of the user password and current date.
                # That way, we ensure that an email/site hash/password hash combination will
                # get a unique reset password link.
                email = self.form.cleaned_data['email']
                user = User.objects.get(email = email)
                h = "%s%s%s%s" % (settings.SECRET_KEY, email, user.password, time.strftime("%Y%m%d"))
                h = hashlib.md5(h).hexdigest()
                reset_link = reverse(ResetPassword.name, args = (h, urllib.quote_plus(email)))

                # Send the invitation (as a signal)
                useraccount = UserAccount.objects.__booster__.get(user__id = user.id)
                reset_password.send(
                    sender = self.__class__,
                    target = useraccount,
                    reset_password_uri = "%s" % (reset_link, ),
                )

                # Say we're happy and redirect
                messages.success(self.request, _("We've sent you a password reset email."))
                raise MustRedirect(reverse("twistranet_home"))
        else:
            self.form = registration_forms.ForgottenPasswordForm()
        
class ResetPassword(AccountLogin):
    """
    Provide a way for users to reset their password.
    Works with a hash generated in the AccountForgottenPassword view.
    """
    name = "reset_password"
    title = _("Reset your password")
    template = "registration/reset_password.html"
    template_variables = BaseView.template_variables + ['form', ]
    
    def prepare_view(self, check_hash, email):
        if self.request.method == "POST":
            self.form = registration_forms.ResetPasswordForm(data=self.request.POST)
            if self.form.is_valid():
                # Generate the reset password link.
                # The link is in two parts: the verification hash and the password hash.
                # That way, we ensure that an email/site hash/password hash combination will
                # get a unique reset password link.
                user = User.objects.get(email = email)
                if user.password == UNUSABLE_PASSWORD:
                    raise ValidationError(_("Can't set password on this user."))
                h = "%s%s%s%s" % (settings.SECRET_KEY, email, user.password, time.strftime("%Y%m%d"))
                h = hashlib.md5(h).hexdigest()
                if not h == check_hash:
                    raise ValidationError("Attempt to access an invalid verification hash.")
                    
                # Actually change password
                user.set_password(self.form.cleaned_data['password'])
                user.save()

                # Say we're happy and redirect
                messages.success(self.request, _("Your password is set to its new value. You can now login."))
                raise MustRedirect(reverse("twistranet_home"))
        else:
            self.form = registration_forms.ResetPasswordForm()
        

class ChangePassword(UserAccountEdit):
    """
    Classic "change password" with former password validation.
    """
    name = "change_password"
    title = _("Change your password")
    template = "account/edit.html"
    form_class = account_forms.ChangePasswordForm
    template_variables = UserAccountEdit.template_variables + ['form', ]
    
    def as_action(self,):
        """
        Display this action only on current account, with user-settable backends.
        """
        if not hasattr(self, "object"):
            return None
        if not self.auth.id == self.object.id:
            return None
        if self.auth.user.password == UNUSABLE_PASSWORD:
            return None
        return super(ChangePassword, self).as_action()

    def prepare_view(self, *args, **kw):
        super(ChangePassword, self).prepare_view(*args, **kw)
        if self.request.method == "POST":
            self.form = account_forms.ChangePasswordForm(data=self.request.POST)
            if self.form.is_valid():
                # Actually change password
                user = self.useraccount.user
                user.set_password(self.form.cleaned_data['new_password'])
                user.save()
        
                # Say we're happy and redirect
                messages.success(self.request, _("New password set."))
                raise MustRedirect(reverse("twistranet_home"))
        else:
            self.form = account_forms.ChangePasswordForm()
    
class AccountLogout(BaseView):
    template = "registration/login.html"
    template_variables = BaseView.template_variables + ["justloggedout", ]
    name = "logout"
    title = _("Logged out")

    def prepare_view(self,):
        messages.info(self.request, mark_safe(_("You are now logged out.<br />Thanks for spending some quality time on Twistranet.")))
        self.justloggedout = True
        logout(self.request)





