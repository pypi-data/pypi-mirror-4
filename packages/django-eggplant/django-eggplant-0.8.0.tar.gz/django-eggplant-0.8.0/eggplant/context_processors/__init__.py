from django.conf import settings
from ground_soil.lang import import_from_string
from eggplant.constants.settings import AJAX_SIGNATURE_KEY_CLASS


def ajax_signature_key(request):
    key_class_path = getattr(settings, AJAX_SIGNATURE_KEY_CLASS, None)

    if key_class_path is not None:
        AjaxSignatureKey = import_from_string(key_class_path)
    else:
        from eggplant.auth.signature import AjaxSignatureKey

    return {'AJAX_REQUEST_SIGNATURE_KEY': AjaxSignatureKey().generator(request)}
