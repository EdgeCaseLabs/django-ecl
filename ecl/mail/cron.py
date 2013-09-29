from django.http import HttpResponse

def process_mail(request):
    
    from ecl.mail.core import process_mail_queue

    count = process_mail_queue()

    return HttpResponse('Done: %s' % count)