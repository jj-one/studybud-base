"""
WSGI config for studybud project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from pathlib import Path
import environ
MY_ENV_DIR = os.path.join(Path(__file__).resolve().parent.parent, '.env')

environ.Env.read_env(MY_ENV_DIR)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studybud.settings')

application = get_wsgi_application()
