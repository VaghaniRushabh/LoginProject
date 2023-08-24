import os

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from fcm_django.models import FCMDevice
from datetime import datetime
from LoginProject.settings import MAX_FILE_SIZE



def content_file_name(instance, filename):
    return os.path.join((type(instance).__name__).lower(), str(instance.id), filename)


def send_email(self, users, context, email=None):
    domain_override = None
    use_https = False
    token_generator = default_token_generator
    email = email if email else self.request.data.get("email")

    if not domain_override:
        current_site = get_current_site(self.request)
        site_name = current_site.name
        domain = current_site.domain
    else:
        site_name = domain = domain_override

    for user in users:
        context.update(
            {
                "email": email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.id)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
            }
        )


def fcm_update(registration_id, device_id, type, user):
    device_data = FCMDevice.objects.filter(device_id=device_id)
    device = device_data.first()
    if device:
        device_data.update(registration_id=registration_id, type=type, user=user)
    else:
        FCMDevice.objects.create(
            device_id=device_id, registration_id=registration_id, type=type, user=user
        )


def validate_file_size(value):
    filesize = value.size
    if filesize >= 1024 * 1024 * MAX_FILE_SIZE:
        raise ValidationError(f"גודל הקובץ שהועלה צריך להיות פחות מ- {MAX_FILE_SIZE}MB")


def get_query_params(request_params):
    query_params = {}
    from_date = None
    end_date = None
    for key, value in request_params.items():
        query_params[key] = value
    selected_role = query_params.get("role-filter", None)
    date_filter = query_params.get("date_filter", None)
    if date_filter:
        from_date = datetime.strptime(date_filter.split("-")[0].strip(), "%Y %m %d")
        end_date = datetime.strptime(date_filter.split("-")[1].strip(), "%Y %m %d")
    return (selected_role, from_date, end_date)
