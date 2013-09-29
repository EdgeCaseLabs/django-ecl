import logging

from django.core.mail import EmailMessage

from .models import MailMessage

def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None):
    """
    Queue mail in MailMessage model.
    """

    from ecl.config.models import GlobalConfig

    if isinstance(recipient_list, list):
        recipient_list = ';'.join(recipient_list)

    #demo override for testing purposes
    demo_recipient_list = GlobalConfig.get_or_none('demo_recipient_list')
    if demo_recipient_list:
        recipient_list = demo_recipient_list

    return MailMessage.objects.create(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
    )

def process_mail_queue():
    """
    Filter all messages of status=active and attempt to send them. Save all exceptions status_details and log.
    :return: Count of active records processed.
    """

    count = 0
    for msg in MailMessage.objects.filter(status=1): #get all active mail in queue
        try:
            recipient_list = msg.recipient_list.split(';')
            outbound = EmailMessage(from_email=msg.from_email, to=recipient_list, subject=msg.subject, body=msg.message)
            outbound.content_subtype = "html"
            outbound.send()
            msg.status = 2 #done
        except Exception, e:
            logging.error('Error sending mail: %s' % e)
            msg.status = 3 #error
            msg.status_details = e

        msg.save()
        count += 1

    return count