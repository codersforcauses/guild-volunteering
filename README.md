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
```
`ALLOWED_HOSTS` should be configured to a list of domains that the server is allowed to serve ([more information](https://docs.djangoproject.com/en/1.10/ref/settings/)).

Additional database settings and engines can be found [here](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-DATABASES)

For development the line `DEBUG = True` can be added to the file.
