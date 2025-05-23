from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


# def send_verification_email(request, user):
#     subject = "请验证您的邮箱"
#     token = default_token_generator.make_token(user)
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#
#     verification_url = request.build_absolute_uri(
#         f"/verify-email/{uid}/{token}/"
#     )
#
#     context = {
#         'user': user,
#         'verification_url': verification_url,
#         'expiry_hours': 24
#     }
#
#     html_message = render_to_string('emails/verify_email.html', context)
#     text_message = render_to_string('emails/verify_email.txt', context)
#
#     send_mail(
#         subject,
#         text_message,
#         'noreply@example.com',
#         [user.email],
#         html_message=html_message,
#         fail_silently=False
#     )