from django.conf.urls.defaults import url, patterns

import kaleo.receivers

from kaleo.views import invite


urlpatterns = patterns("",
    url(r"^invite/$", invite, name="kaleo_invite"),
)
