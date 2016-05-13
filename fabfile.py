__author__ = 'leonhard'

from fabric.api import run


def update():
    run('cd /srv/roomer/roomer')
    run('git checkout .')
    run('git checkout master')
    run('git pull')
    run('source ../venv/bin/activate')

    run('pip install -r requirements.txt')

    run('python manage_prod.py makemigrations roomer collegechoosre allocation')
    run('python manage_prod.py migrate')
    run('python manage_prod.py collectstatic --no-input')

    run('supervisorctl reread')
    run('supervisorctl update')
