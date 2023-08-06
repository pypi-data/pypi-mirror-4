Rosetta Inpage
==============
Django app on top of Django Rosetta, it enables you to translate in webpages directly.
It patches the default `gettext` functionality to capture all messages rendered on a page.

Installation
------------
Rosetta Inpage requires Django 1.3 or later and Django Rosetta 0.6.8.

1. Add to your requirements: 
```
django-rosetta==0.6.8
rosetta_inpage==0.0.1
```

2. Add to installed apps:
```
INSTALLED_APPS = (
    ...
    'rosetta',
    'rosetta_inpage',
    ...
)
```

3. Add the middleware:
```
MIDDLEWARE_CLASSES = (
    ...
    'rosetta_inpage.middleware.TranslateMiddleware',
    ...
)
```

4. Add some settings, `ROSETTA_INPAGE` enables/disables the inpage plugin, set to `False` in production:
```
##
## Rosetta config
## https://github.com/mbi/django-rosetta
##
ROSETTA_MESSAGES_PER_PAGE = 50
ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True
ROSETTA_MESSAGES_SOURCE_LANGUAGE_CODE = "en"
ROSETTA_MESSAGES_SOURCE_LANGUAGE_NAME = "English"
ROSETTA_STORAGE_CLASS = "rosetta.storage.CacheRosettaStorage"
ROSETTA_INPAGE = True   
```

5. Last but not least, apply a magical patch in your settings.  It will patch the default `gettext` functionality:
```
from rosetta_inpage.patches import patch_ugettext
patch_ugettext()
```

6. Add URL entry to your project's `urls.py`, for example:
```
    url(r'^rosetta_inpage/', include('rosetta_inpage.urls')),
    url(r'^rosetta_inpage/', include('rosetta.urls')),
```