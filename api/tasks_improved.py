"""
============================================================================
نسخة محسّنة من api/tasks.py — إضافة آلية إعادة المحاولة (Retry) لإرسال
الإيميل، بدل الاعتماد على نجاحه من أول محاولة فقط.

الفكرة: لو send_mail() فشلت (انقطاع شبكة مؤقت، SMTP server بطيء أو
مشغول، Timeout...)، بدل ما الـ task تفشل نهائياً وبصمت، Celery يعيد
جدولتها تلقائياً بعد فترة انتظار (countdown)، لعدد محاولات محدد
(max_retries) قبل الاستسلام النهائي.
============================================================================
"""

import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_email(self, order_id, user_email):
    """
    يرسل إيميل تأكيد الطلب، مع إعادة محاولة تلقائية حتى 3 مرات
    (بفاصل 60 ثانية بين كل محاولة) لو فشل الإرسال لسبب مؤقت.

    - bind=True: يعطي الدالة الوصول لـ self (نسخة الـ task نفسها)،
      وهذا ضروري لاستدعاء self.retry(...) لاحقاً.
    - max_retries=3: بعد 3 محاولات فاشلة، تتوقف الـ task نهائياً
      ويُسجَّل الفشل بدل إعادة المحاولة إلى ما لا نهاية.
    - default_retry_delay=60: مدة الانتظار الافتراضية (بالثواني)
      قبل كل محاولة إعادة، قابلة للتجاوز عبر countdown= عند الاستدعاء.
    """
    subject = 'Order Confirmation'
    message = f'Your order with ID {order_id} has been received and is being processed.'

    try:
        return send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

    except Exception as exc:
        logger.warning(
            f"Failed to send confirmation email for order {order_id} "
            f"(attempt {self.request.retries + 1}/{self.max_retries + 1}): {exc}"
        )
        try:
            # يعيد جدولة نفس الـ task تلقائياً بعد default_retry_delay ثانية.
            # exc=exc يحفظ سبب الفشل الأصلي ضمن معلومات الـ task.
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            # استُنفدت كل المحاولات (3 من 3) — نسجّل فشل نهائي بدل
            # ابتلاعه بصمت، حتى لو المستخدم نفسه لن يرى هذه الرسالة.
            logger.error(
                f"Giving up on confirmation email for order {order_id} "
                f"after {self.max_retries + 1} attempts."
            )
            # اختياري: يمكن هنا إشعار فريق الدعم، أو تسجيل الطلب
            # بجدول "إيميلات فشلت" لإعادة الإرسال يدوياً لاحقاً.
            return None
