from app.models import CustomUser
import logging
from .relations import friendsContext
from .dashboard import get_game_history_and_stats
from app.forms import DeleteAccountForm, UpdatePasswordForm, UpdateEmailForm, UpdateNameForm, UploadImageForm


logger = logging.getLogger(__name__)


def get_profile_details(username:str, self:bool) -> dict:
    details = {}
    user = CustomUser.objects.filter(username=username)
    logger.debug(user[0])
    if not user:
        details["error"] = "No users in system match the requested user"
    else:
        details["username"] = username
        details["first_name"] = user[0].first_name
        details["last_name"] = user[0].last_name
        if self:
            details["email"] = user[0].email
    # details["img"] = user.img #how to get link for profile image?
    # print(details)
    return details


def profileContext(username:str, self:bool) -> dict:
    logger.debug('in profileContext')
    context = {}
    context["friends"] = friendsContext(username, None, None)
    context["details"] = get_profile_details(username, self)
    context["name_form"] = UpdateNameForm()
    context["email_form"] = UpdateEmailForm()
    context["password_form"] = UpdatePasswordForm()
    context["delete_account_form"] = DeleteAccountForm()
    context["upload_image_form"] = UploadImageForm()
    context["self_profile"] = self
    history, stats = get_game_history_and_stats(username)
    logger.debug("values in profileContext: ")
    logger.debug(history)
    logger.debug(stats)
    context["stats"] = stats
    context["history"] = history
    try:
        profile_user = CustomUser.objects.filter(username=username).first()
        if profile_user:
            context["profile_picture"] = profile_user.profile_picture
    except Exception as e:
        logger.debug('error: ', e)
        context['error'] = e
        logger.debug('unable to search image')
    return context