# Guild Volunteering
An alternative to physical logbooks for Guild Volunteering UWA to allow students to enter their volunteering hours.

The django project requires that some local setting be configured for database access. 
To do this create a new file in the gvs directory called `local_settings.py`

**Example contents for a mysql server:**

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DatabaseName',
        'USER': 'DatabaseUser',
        'PASSWORD': 'DatabasePassword',
        'HOST': '127.0.0.1'
    }
}
ALLOWED_HOSTS = ['127.0.0.1']

EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='<EMAIL HOST>'
EMAIL_PORT='<EMAIL_PORT>'
EMAIL_HOST_USER='<YOUR EMAIL ADDRESS>'
EMAIL_HOST_PASSWORD='<PASSWORD FOR EMAIL>'
EMAIL_USE_TLS=True
```
`ALLOWED_HOSTS` should be configured to a list of domains that the server is allowed to serve ([more information](https://docs.djangoproject.com/en/1.10/ref/settings/)).

`EMAIL_HOST` Should be the service which hosts your email address e.g. smtp.google.com .

`EMAIL_PORT` The port which the service runs on.

Additional database settings and engines can be found [here](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-DATABASES)

For development the line `DEBUG = True` can be added to the file.

## Requirements:
Need to install:
- [django-datetime-widget](https://github.com/asaglimbeni/django-datetime-widget)
- [django-adminplus](https://github.com/jsocol/django-adminplus)

## Testing
To run the tests use
```python manage.py test logbook/tests```

## Use:
- Only get students so finalise logbooks at the end of semester, so they can still volunteer for an organisation.