# -*- coding: utf-8 -*-
import sys
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models.loading import get_models, get_app
from quickview.management.commands.template_base import get_templates

class Command(BaseCommand):
    args = 'app_label model_name1 model_name2 model_name3 etc'
    help = 'Creates templates for models listed related to specified app.'

    def handle(self, *args, **options):
        if not args:
            print(help)
            sys.exit(1)

        app_label = args[0]
        models_to_process = args[1:]
        if not models_to_process:
            print("No models supplied.")
            sys.exit(1)

        apps = [ app for app in settings.INSTALLED_APPS if not "django" in app and not "quickview" in app]
        if not app_label in apps:
            print("No such app '%s'." % app_label)
            sys.exit(1)

        models = get_models(get_app(app_label))
        for model in models_to_process:
            if not model in [f.__name__ for f in models]:
                print("No such model '%s' for app '%s'." % (model, app_label))
                sys.exit(1)

        folder = os.path.join(os.path.abspath(os.curdir), app_label)
        if not os.path.exists(folder):
            print("Could not find '%s' for app '%s'" % (folder, app_label))
            sys.exit(1)

        # write views in views.py
        views_file = os.path.join(folder, 'views.py')
        if not os.path.exists(views_file):
            views_file = os.path.join(folder, 'views', '__init__.py')
            if not os.path.exists(views_file):
                print("Could not find any views.py or views-folder for app '%s'" % app_label)
                sys.exit(1)

        lines = open(views_file).readlines()
        if not 'from quickview import ModelQuickView\n' in lines:
            lines.insert(0, "from quickview import ModelQuickView\n")

        for model_name in models_to_process:
            if "from %s.models import %s\n" % (app_label, model_name) in lines:
                continue

            lines.insert(1, "from %s.models import %s\n" % (app_label, model_name))

            if not 'class %sView(ModelQuickView):\n' % model_name in lines:
                lines.append("\n\n")
                for model_name in models_to_process:
                    lines.append("class %sView(ModelQuickView):\n" % model_name)
                    lines.append("    model = %s\n" % model_name)
                    lines.append("    use_dynamic_ajax_page = True\n")
                    lines.append("    use_pagination = True\n")
                    lines.append("    items_per_page = 5\n")
                    lines.append("    #authentication_required = True\n\n\n")

        open(views_file, 'w').writelines(lines)

        template_folder = os.path.join(folder, 'templates')
        if not os.path.exists(template_folder):
            os.makedirs(template_folder)

        # create folders
        for model_name in models_to_process:
            tf = os.path.join(template_folder, app_label, model_name)
            if os.path.exists(tf):
                print("Template folder for model '%s' exists. Will exit." % model_name)
                sys.exit(1)
            os.makedirs(tf)
            index_template, delete_template, add_template, update_template, \
            detail_template, base_site_template = get_templates(app_label, model_name)

            open(os.path.join(tf, 'base_site.html'), 'w').write(base_site_template)
            open(os.path.join(tf, 'index.html'), 'w').write(index_template)
            open(os.path.join(tf, 'detail.html'), 'w').write(detail_template)
            open(os.path.join(tf, 'add.html'), 'w').write(add_template)
            open(os.path.join(tf, 'update.html'), 'w').write(update_template)
            open(os.path.join(tf, 'delete.html'), 'w').write(delete_template)

        self.stdout.write('Successfully created initial data.')
