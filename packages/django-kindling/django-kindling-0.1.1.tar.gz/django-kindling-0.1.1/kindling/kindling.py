import os
import sys
from jinja2 import Environment, PackageLoader
from subprocess import Popen
env = Environment(loader=PackageLoader('kindling', 'templates'))

FILES = (
    ('.gitignore', False),
    ('config.rb', False),
    ('requirements.txt', False),
    ('fabfile.py', False),
    ('settings/__init__.py', True),
    ('settings/base.py', True),
    ('settings/development.py', True),
    ('settings/local.py', True),
    ('settings/production.py', True),
    ('settings/celery_development.py', True),
    ('settings/celery_local.py', True),
    ('settings/celery_production.py', True),
    ('static/javascripts/default.build.js', True),
    ('static/javascripts/jquery.cookie.js', True),
    ('static/javascripts/main.build.js', True),
    ('static/javascripts/main.js', True),
)

def generate(app, path, in_app=False):
    print(u'Generating {}'.format(path))
    template = env.get_template(path)
    path = os.path.split(path)
    data = template.render(app=app)
    path = [app] + list(path)
    if in_app:
        path.insert(0, app)
    directory = os.path.join(*path[:-1])
    if not os.path.exists(directory):
        print("Made dir {}".format(directory))
        os.makedirs(directory)
    with open(os.path.join(*path), 'w') as f:
        f.write(data)

def new(app):
    os.unsetenv('DJANGO_SETTINGS_MODULE')
    if not app:
        print('App must be set.')
        sys.exit()
    
    if os.path.exists(app):
        print('App already exists.')
        sys.exit()
    
    p = Popen(['django-admin.py', 'startproject', app])
    p.wait()

    p = Popen(['git', 'init', app])
    p.wait()
    
    os.remove(os.path.join(app, app, 'settings.py'))
    for args in FILES:
        generate(app, *args)

    virtual_env = os.environ.get('VIRTUAL_ENV', None)
    if virtual_env:
        with open(os.path.join(virtual_env, 'bin', 'postactivate'), 'w') as f:
            f.write('#!/bin/zsh\nexport DJANGO_SETTINGS_MODULE={app}.settings.local'.format(app=app))


def main():
    new(sys.argv[1])


if __name__ == '__main__':
    main()
