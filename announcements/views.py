from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User

from .forms import AnnouncementForm
from .models import Announcement


def _is_admin_user(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff or user.role == User.ROLE_ADMIN)


@login_required
def announcement_list_view(request):
    announcements = Announcement.objects.select_related("created_by").all()
    is_admin = _is_admin_user(request.user)
    return render(
        request,
        "announcements/list.html",
        {
            "announcements": announcements,
            "is_admin": is_admin,
        },
    )


@user_passes_test(_is_admin_user)
def announcement_create_view(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, "Announcement posted successfully.")
            return redirect("announcements:list")
    else:
        form = AnnouncementForm()

    return render(
        request,
        "announcements/form.html",
        {
            "form": form,
            "page_title": "Create Announcement",
            "submit_label": "Post Announcement",
        },
    )


@user_passes_test(_is_admin_user)
def announcement_update_view(request, announcement_id):
    announcement = get_object_or_404(Announcement, pk=announcement_id)

    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement updated successfully.")
            return redirect("announcements:list")
    else:
        form = AnnouncementForm(instance=announcement)

    return render(
        request,
        "announcements/form.html",
        {
            "form": form,
            "page_title": "Edit Announcement",
            "submit_label": "Save Changes",
        },
    )


@user_passes_test(_is_admin_user)
def announcement_delete_view(request, announcement_id):
    announcement = get_object_or_404(Announcement, pk=announcement_id)

    if request.method == "POST":
        announcement.delete()
        messages.success(request, "Announcement deleted successfully.")
        return redirect("announcements:list")

    return render(
        request,
        "announcements/confirm_delete.html",
        {"announcement": announcement},
    )
