from app.models import CustomUser
import logging
from .relations import friendsContext
from .dashboard import get_game_history_and_stats
from app.forms import DeleteAccountForm, UpdatePasswordForm, UpdateEmailForm, UpdateNameForm, UploadImageForm


logger = logging.getLogger(__name__)


def get_profile_details(username:str, self:bool) -> dict:
    details = {}
    user = CustomUser.objects.filter(username=username).first()
    if user is None:
        details["error"] = "No users in system match the requested user"
    else:
        details["username"] = username
        details["first_name"] = user.first_name
        details["last_name"] = user.last_name
        if self:
            details["email"] = user.email
    return details


def profileContext(username:str, self:bool) -> dict:
    context = {}
    context["active"] = "profile"
    context["friends"] = friendsContext(username, None, None)
    context["details"] = get_profile_details(username, self)
    context["name_form"] = UpdateNameForm()
    context["email_form"] = UpdateEmailForm()
    context["password_form"] = UpdatePasswordForm()
    context["delete_account_form"] = DeleteAccountForm()
    context["upload_image_form"] = UploadImageForm()
    context["self_profile"] = self
    history, stats = get_game_history_and_stats(username)
    context["stats"] = stats
    context["history"] = history
    try:
        profile_user = CustomUser.objects.filter(username=username).first()
        if profile_user:
            context["profile_picture"] = profile_user.profile_picture
    except Exception as e:
        logger.error('error in profile context: ', e)
        context['error'] = e
    return context

def get_profile_picture_context(username:str):
    """
    returns context to render the prfile_picture.html template
    """
    current_user = CustomUser.objects.filter(username=username).first()
    context = {}
    context["username"] = username
    if not current_user:
        return context
    context["profile_picture"] = current_user.profile_picture
    return context


def user_exists(username:str) -> bool:
    user = CustomUser.objects.filter(username=username)
    if not user.first():
        return False
    else:
        return True