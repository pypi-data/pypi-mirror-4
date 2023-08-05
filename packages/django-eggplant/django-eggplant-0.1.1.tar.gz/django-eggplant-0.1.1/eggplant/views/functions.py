from django.http import HttpResponse

def lack_of_required_key_default_handler(request, key, *args, **kwargs):
    response = HttpResponse()
    response['Content-Type'] = 'text/plain'
    response.status_code = 400
    response.content = 'Key "%s" is required.' % key
    return response

def key_validation_failed_default_handler(request, key, *args, **kwargs):
    response = HttpResponse()
    response['Content-Type'] = 'text/plain'
    response.status_code = 400
    response.content = 'Key "%s" is invalid.' % key
    return response
