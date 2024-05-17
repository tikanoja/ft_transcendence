from app.forms import RegistrationForm, DeleteAccountForm, UpdatePasswordForm, UpdateEmailForm, UpdateNameForm, UploadImageForm
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from app.models import CustomUser, CustomUserManager, GameInstance, Friendship, Tournament, Match
from .profile import get_profile_details
import os
from transcendence import settings
import logging
from django.db.models import Q
from PIL import Image, ImageFile
import io


logger = logging.getLogger(__name__)


def create_manage_account_context(username: str) -> dict:
    context = {}
    # context["details"] = get_profile_details(username, self) want to add after any updates
    context["name_form"] = UpdateNameForm()
    context["email_form"] = UpdateEmailForm()
    context["password_form"] = UpdatePasswordForm()
    context["delete_account_form"] = DeleteAccountForm()
    context["upload_image_form"] = UploadImageForm()
    return context


def	registerPOST(request):
    title = "Register as a new user"
    sent_form = RegistrationForm(request.POST)
    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        logger.debug(f"Error in registration form: {ve}")
        return render(request, 'user/register.html', {"form": sent_form, "title": title, "error": ve})
    new_user = get_user_model()
    new_user.objects.create_user(username=sent_form.cleaned_data['username'], email=sent_form.cleaned_data['email'], password=sent_form.cleaned_data['password'], first_name=sent_form.cleaned_data['first_name'], last_name=sent_form.cleaned_data['last_name'])
    res = JsonResponse({'success': "account created"}, status=301)
    next = request.GET.get('next', '/login')
    if next:
        res['Location'] = next
    return res


def registerGET(request):
    title = "Register as a new user"
    form = RegistrationForm()
    return render(request, 'user/register.html', {"form": form, "title": title})


def tournament_deleted_user(user):
    tournament = Tournament.objects.filter(Q(status=Tournament.ACTIVE), Q(participants=user)).first()
    matches = Match.objects.filter(tournament=tournament, status=Match.SCHEDULED)
    for match in matches:
        game_instance = match.game_instance

        if game_instance.p1 == user:
            game_instance.p1 = None
            game_instance.winner = game_instance.p2
        elif game_instance.p2 == user:
            game_instance.p2 = None
            game_instance.winner = game_instance.p1
        else:
            continue
        
        game_instance.status = GameInstance.FINISHED
        game_instance.save()
        match.status = Match.FINISHED
        match.save()

def delete_accountPOST(request, context):
    if request.user.is_authenticated:
        context["details"] = get_profile_details(request.user.username, True)
        delete_form = DeleteAccountForm(request.POST)
        try:
            if not delete_form.is_valid():
                raise ValidationError("Values given are not valid") 
        except ValidationError as ve:
            context["form"] = delete_form
            context["error"] = ve
            return render(request, "user/profile_partials/manage_account.html", context)
        username = request.user
        password = delete_form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # check if this should cascade delete the profile etc. remove from friend lists...
            tournament_deleted_user(user)
            Friendship.objects.filter(from_user=username).delete()
            Friendship.objects.filter(to_user=username).delete()
            GameInstance.objects.filter(p1=username, status='Pending').delete()
            GameInstance.objects.filter(p2=username, status='Pending').delete()
            GameInstance.objects.filter(p1=username, status='Accepted').delete()
            GameInstance.objects.filter(p2=username, status='Accepted').delete()
            CustomUser.objects.filter(username=username).delete()
            # delete account, return a success page with a 'link' to go to homepage
            return JsonResponse({'message': 'Your account has been deleted'})
        else:
            context["error"] = 'Unable to delete account. Check which account you are logged in as'
            return render(request, "user/profile_partials/manage_account.html", context)
    else:
        context["error"] = 'User needs to be logged into delete account'
        return render(request, "user/profile_partials/manage_account.html", context)
    

def manage_accountPOST(request):
    user_manager = CustomUserManager()
    logger.debug(request.POST)
    context = create_manage_account_context(request.user.username)
    if "name-change-form" == request.POST['form_id']:
        logger.debug("name change form found")
        form = UpdateNameForm(request.POST)
        try:
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly")
            user_manager.update_user(request.user.username, first_name=form.cleaned_data["first_name"], last_name=form.cleaned_data["last_name"])
            context["name_form_result"] = 'Name updated successfully'
        except ValidationError as ve:
            context["error"] = ve
            context["name_form"] = form
    elif "email-change-form" == request.POST['form_id']:
        logger.debug("email change form found")
        form = UpdateEmailForm(request.POST)
        try:
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly")
            user_manager.update_user(request.user.username, email=form.cleaned_data["email"])
            context['email_form_result'] = 'Email updated successfully'
        except ValidationError as ve:
            context["error"] = ve
            context["email_form"] = form 
    elif "password-change-form" == request.POST['form_id']:
        logger.debug("password change form found")
        form = UpdatePasswordForm(request.POST)
        try:
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly")
            user_manager.update_user(request.user.username, password=form.cleaned_data["password"])
            context['pasword_form_result'] = 'Password updated successfully. Please log back in with your new password'
        except ValidationError as ve:
            context["error"] = ve
            context["email_form"] = form 
    elif "delete-account-form" == request.POST['form_id']:
        return delete_accountPOST(request, context)
    elif "profile_picture_upload" == request.POST['form_id']:
        form = UploadImageForm(request.POST, request.FILES)
        try:
            current_user = CustomUser.objects.get(username=request.user.username)
            new_image = request.FILES['profile_picture']
            old_image = current_user.profile_picture
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly for profile picture")

            # Resizing the uploaded img to be 300x300 while maintaining aspect ratio
            img = Image.open(new_image)
            if img.mode!= 'RGB':
                img = img.convert('RGB')
            max_size = (300, 300)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            in_mem_file = io.BytesIO()
            img.save(in_mem_file, format='JPEG')
            in_mem_file.seek(0)
            new_image.file = in_mem_file

            if old_image.url != '/media/default.png':
                os.remove(os.path.join(settings.MEDIA_ROOT, old_image.path))
            current_user.profile_picture = new_image
            current_user.save()
            context['profile_picture_upload_message'] = 'new image uploaded!'
        except Exception as e:
            context["error"] = e
            context["profile_picture_upload"] = form 
    else:
        context["error"] = 'Invalid form submitted'
    context["details"] = get_profile_details(request.user.username, True)
    return render(request, "user/profile_partials/manage_account.html", context)