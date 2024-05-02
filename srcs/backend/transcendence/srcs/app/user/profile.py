from app.models import CustomUser
import logging


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


def next_one():
    pass