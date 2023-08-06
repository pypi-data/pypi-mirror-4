# -*- coding: utf-8 -*-
import os

from jinja2 import Environment, PackageLoader

from django_deployer.helpers import _write_file

from fabric.operations import local
from fabric.context_managers import shell_env


template_env = Environment(loader=PackageLoader('django_deployer', 'paas_templates'))


class PaaSProvider(object):
    """
    Base PaasProvider class. PaaS providers should inherit from this
    class and override all methods.
    """

    # Subclasses should override these
    name = ""
    setup_instructions = ""
    PYVERSIONS = {}
    provider_yml_name = "%s.yml" % name

    @classmethod
    def init(cls, site):
        cls._create_configs(site)
        print cls.setup_instructions

    @classmethod
    def deploy(cls):
        raise NotImplementedError()

    @classmethod
    def delete(cls):
        raise NotImplementedError()

    @classmethod
    def _create_configs(cls, site):
        """
        This is going to generate the following configuration:
        * wsgi.py
        * <provider>.yml
        * settings_<provider>.py
        """
        provider = cls.name

        cls._render_config('wsgi.py', 'wsgi.py', site)

        yaml_template_name = os.path.join(provider, cls.provider_yml_name)
        cls._render_config(cls.provider_yml_name, yaml_template_name, site)

        settings_template_name = os.path.join(provider, 'settings_%s.py' % provider)
        settings_path = site['django_settings'].replace('.', '/') + '_%s.py' % provider
        cls._render_config(settings_path, settings_template_name, site)

    @classmethod
    def _render_config(cls, dest, template_name, template_args):
        """
        Renders and writes a template_name to a dest given some template_args.

        This is for platform-specific configurations
        """
        template_args = template_args.copy()

        # Substitute values here
        pyversion = template_args['pyversion']
        template_args['pyversion'] = cls.PYVERSIONS[pyversion]

        template = template_env.get_template(template_name)
        contents = template.render(**template_args)
        _write_file(dest, contents)


class Stackato(PaaSProvider):
    """
    ActiveState Stackato PaaSProvider.
    """
    name = "stackato"

    PYVERSIONS = {
        "Python2.7": "python27",
        "Python3.2": "python32",
    }

    setup_instructions = """
Just a few more steps before you're ready to deploy your app!

1. Go to http://www.activestate.com/stackato/download_client to download
   the Stackato client, and then add the executable somewhere in your PATH.
   If you're not sure where to place it, you can simply drop it in your
   project's root directory (the same directory as the fabfile.py created
   by django-deployer).

2. Once you've done that, target the stackato api with:

       stackato target api.stacka.to

   and then login. You can find your sandbox password at
   https://account.activestate.com, which you'll need when
   using the command:

       stackato login --email <email>

3. You can push your app the first time with:

       stackato push -n

   and make subsequent updates with:

       stackato update

"""

    def init():
        pass

    def deploy():
        pass

    def delete():
        pass


class DotCloud(PaaSProvider):
    """
    Dotcloud PaaSProvider.
    """
    name = "dotcloud"

    PYVERSIONS = {
        "Python2.6": "v2.6",
        "Python2.7": "v2.7",
        "Python3.2": "v3.2",
    }

    @classmethod
    def init(cls, site):
        super(DotCloud, cls).init(site)

        cls._render_config('createdb.py', os.path.join(cls.name, 'createdb.py'), site)
        cls._render_config('mkadmin.py', os.path.join(cls.name, 'mkadmin.py'), site)
        cls._render_config('nginx.conf', os.path.join(cls.name, 'nginx.conf'), site)
        cls._render_config('postinstall', os.path.join(cls.name, 'postinstall'), site)

    def deploy():
        pass

    def delete():
        pass


class AppEngine(PaaSProvider):
    """
    AppEngine PaaSProvider
    """

    name = 'appengine'

    PYVERSIONS = {
        "Python2.7": "v2.7"
    }

    setup_instructions = """
Just a few more steps before you're ready to deploy your app!

1. Run this command to create the virtualenv with all the packages and deploy:

        $ fab deploy

2. Create and sync the db on the Cloud SQL:

        $ sh manage.sh cloudcreatedb
        $ sh manage.sh cloudsyncdb

3. Everything is set up now, you can run other commands that will execute on your remotely deployed app, such as:

        $ sh manage.sh dbshell

"""

    provider_yml_name = "app.yaml"

    @classmethod
    def init(cls, site):
        super(AppEngine, cls).init(site)

        # config_list: files to put in project folder, django_config_list: files to put in django project folder
        config_list = ['requirements_deploy.txt', 'manage.sh']
        django_config_list = ['urls_appengine.py']

        # for rendering configs under root
        get_config = lambda filename: cls._render_config(filename, os.path.join(cls.name, filename), site)
        map(get_config, config_list)

        # for rendering configs under django project folder
        get_django_config = lambda filename: cls._render_config("%s/%s"%(site['project_name'], filename), os.path.join(cls.name, filename), site)
        map(get_django_config, django_config_list)

    @classmethod
    def deploy(cls, site):
        """
        tasks:
            * collect statics
            * fetch all the required libraries from pip (require_deploy.txt)
            * deploy
        """
        # Create virtual environment
        # TODO: detect whether it is a virtualenv
        if not os.path.isdir("env"):
            print "Detected there is no any virtual environment, going to create one..."
            local("virtualenv --no-site-packages env")

        # install requirements for deployment
        local("env/bin/pip install -r %(requirements)s" % site)
        local("env/bin/pip install -r requirements_deploy.txt")

        # Collects static files into static folder
        local("sh manage.sh collectstatic --noinput")

        # deploy
        local("sh manage.sh deploy")

    def delete():
        pass


PROVIDERS = {
    'stackato': Stackato,
    'dotcloud': DotCloud,
    'appengine': AppEngine
}
