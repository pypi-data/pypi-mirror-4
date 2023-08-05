from os.path import join
from django.conf import settings
import canjs

def canjs_urls(library=None, version=None, extras=None):
    if not version:
        version = getattr(settings, "CANJS_VERSION", canjs.__version__)
    jquery_version = getattr(settings, "CANJS_JQUERY_VERSION", canjs.__jquery_version__)

    L = []
    if extras is not None:
        if "jquery" in extras:
            if settings.DEBUG:
                L.append(join(settings.STATIC_URL, "canjs/jquery", jquery_version, "jquery.js"))
            else:
                L.append(join(settings.STATIC_URL, "canjs/jquery", jquery_version, "jquery.min.js"))
            del extras[extras.index("jquery")]
        if "csrf" in extras:
            L.append(join(settings.STATIC_URL, "canjs", "csrf.js"))
            del extras[extras.index("csrf")]
        if "json2" in extras:
            L.append(join(settings.STATIC_URL, "canjs", "json2.js"))
            del extras[extras.index("json2")]

    if not library:
        library = "jquery"

    if settings.DEBUG:
        L.append(join(settings.STATIC_URL, "canjs", version, "can.%s.js" % library))
    else:
        L.append(join(settings.STATIC_URL, "canjs", version, "can.%s.min.js" % library))

    if extras:
        for e in extras:
            L.append(join(settings.STATIC_URL, "canjs", version, "can.%s.js" % e))

    return L
