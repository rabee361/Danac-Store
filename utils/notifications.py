from base.models import UserNotification
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification



def send_product_notification(user,title,body,details=None):
    if user.get_notifications:
        devices = FCMDevice.objects.filter(user=user.id)

        devices.send_message(
            message=Message(
                notification=Notification(
                    title=title,
                    body=body
                ),
            ),
        )
        UserNotification.objects.create(
            user = user,
            title = title,
            body = body,
            details={
                "product_id":details
            }
        )     




def send_order_notification(user,details):
    if user.get_notifications:
        devices = FCMDevice.objects.filter(user=user.id)
        title = 'انشاء طلب'
        body = f'تم ارسال طلبك بنجاح'
        devices.send_message(
                message =Message(
                    notification=Notification(
                        title=title,
                        body=body
                    ),
                ),
            )
        UserNotification.objects.create(
            user=user,
            body=body,
            title=title,
            details={
                "order_id":details
            }

        )
