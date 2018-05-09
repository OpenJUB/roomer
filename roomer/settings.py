"""
Django settings for roomer project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os, csv



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

eligible_people = []

#importing CSV file
csv_file = os.path.join(BASE_DIR, "eligible_students.csv")
with open(csv_file, 'r', encoding='latin_1') as f:
    render = csv.reader(f, delimiter=';')
    for row in render:
        if len(row) >= 3:
            eligible_people.append(row[1] + (' ' if row[2] else '') + row[2] + ' ' + row[0])

for entry in eligible_people:
    print("Eligible person: '{}'".format(entry))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2&h!5qkb4)d$#@@tn5umls)mwniq55l3q*iv)lxc2y(avkmx9v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
    'collegechooser',
    'roommates',
    'roomer',
    'allocation',
    'faq',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dreamjub.providers.oauth',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'roomer.urls'
LOGIN_REDIRECT_URL = "home"

STATICFILES_DIRS= [
    os.path.join(BASE_DIR, "static")
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'roomer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Only send emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'exchange.jacobs-university.de'

# For admin notifications
SERVER_EMAIL = 'system@roomer.jacobs.university'
ADMINS = [
        ('Leonhard', 'l.kuboschek@jacobs-university.de'),
        ('Sid', 's.shukla@jacobs-university.de')
]


# Used for generating full URL in email templates
EMAIL_DOMAIN = 'http://roomer.jacobs.university'

# Custom User model
AUTH_USER_MODEL = "roomer.UserProfile"

# OpenJUB auth
AUTHENTICATION_BACKENDS = ( 'django.contrib.auth.backends.ModelBackend',
                            'allauth.account.auth_backends.AuthenticationBackend')
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'

MAX_RACE_QUOTA = 0.2
SOCIALACCOUNT_ADAPTER = 'roomer.adapter.DreamjubAdapter'



LOGIN_URL = "dreamjub_login"
LOGIN_REDIRECT_URL = "home"

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

COLLEGE_CODES = ['', 'NM', 'ME', 'KR', 'C3']

# College choices /short_name, long_name, capacity)
COLLEGE_CHOICES = [
    ('NM', 'Nordmetall'),
    ('C3', 'C3'),
    ('KR', 'Krupp'),
    ('ME', 'Mercator')
]

COLLEGE_CAPACITIES = [
    ('NM', 257),
    ('C3', 246),
    ('KR', 188),
    ('ME', 188)
]

# types of students
HOUSING_TYPE_UNKNOWN = 'Unknown'
HOUSING_TYPE_FRESHIE = 'Freshie'
HOUSING_TYPE_FOUNDATION_YEAR = 'Foundation Year'
HOUSING_TYPE_UG_1 = '1st Year (Undergrad)'
HOUSING_TYPE_UG_2 = '2nd Year (Undergrad)'
HOUSING_TYPE_UG_3 = '3rd+ Year (Undergrad)'
HOUSING_TYPE_MS_1 = '1st Year (Master)'
HOUSING_TYPE_MS_2 = '2nd+ Year (Master)'

HOUSING_TYPES = [
    (0, HOUSING_TYPE_UNKNOWN),
    (1, HOUSING_TYPE_FRESHIE),

    (2, HOUSING_TYPE_FOUNDATION_YEAR),

    (3, HOUSING_TYPE_UG_1),
    (4, HOUSING_TYPE_UG_2),
    (5, HOUSING_TYPE_UG_3),

    (6, HOUSING_TYPE_MS_1),
    (7, HOUSING_TYPE_MS_2),
]

# Maximum filling of the college, in percent
MAX_COLLEGE_FILL = 75

# Used for generating freshie accounts
FRESHIE_USERNAME = 'ffreshface'
