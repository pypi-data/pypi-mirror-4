# django-userpure

Basic feature set for managing users in Django 1.5.
With the deprecation of user profiles and the growth of 
custom user models, the need for a new user management system
was necessary.

## Installation

To install ``django-userpure``, download django-userpure and run:

    python setup.py insatll

## Usage

The following is an example of how to use the Activation feature:

``models.py``:

    class UserManager(UserpureActivationManager, BaseUserManager):
        def create_user(self, email, password, **extra_fields):
            now = timezone.now()
            if not email:
                raise ValueError('The given email must be set')
            email = UserManager.normalize_email(email)
            user = self.model(email=email, is_active=True, is_superuser=False, last_login=now, **extra_fields)

            user.set_password(password)
            user.save(using=self._db)
            return user

    class User(UserpureActivationMixin, PermissionsMixin, AbstractBaseUser):
        objects = UserManager()

        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = []

``views.py``:

    class Activate(View):
        """
        Activate a user by activation key.
        """
        activation_key = None
        user = None
        redirect_url = None
        
        def get(self, request):
            self.activation_key = request.GET.get('activation_key', None)
            if self.activation_key:
                self.user = get_user_model().objects.activate(self.activation_key)
                if self.user:
                    messages.success(request, _("User activated successfully."))
                else:
                    messages.error(request, _("Could not activate user."))
            return HttpResponseRedirect(self.redirect_url)

## Design
The idea is that any amount of functionality can be mixed into managers or models.
Since there are two types of forms, mixins can be danerous to use with forms.
This is largely why forms are left out of the picture for now.

### Available models
1. ``UserpureActivationMixin`` enables activation of a user.

### Available managers
1. ``UserpureActivationManager`` enables activation of a user through a manager.