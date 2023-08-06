from hashlib import sha1
import hmac
import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import signals

def valid_request(request):
    """
    Verifies the integrity of the facebook callback by validating the hashed
    message authentication code of the request body matches the value passed 
    in the X-Hub-Signature header header.

    Returns True if request checks out
    """
    fb_sig = signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    request_sig = hmac.new(settings.FACEBOOK_API_SECRET, request.body, sha1)
    return fb_sig == 'sha1=' + request_sig.hexdigest()

@csrf_exempt
def callback(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        challenge = request.GET.get('hub.challenge')
        verify_token = request.GET.get('hub.verify_token')
        if settings.FACEBOOK_VERIFY_TOKEN == verify_token:
            return HttpResponse(challenge)
    else:
        if valid_request(request):
            updates = json.loads(request.body)
            signals.fb_update.send(sender=None, updates=updates)

    return HttpResponse()

