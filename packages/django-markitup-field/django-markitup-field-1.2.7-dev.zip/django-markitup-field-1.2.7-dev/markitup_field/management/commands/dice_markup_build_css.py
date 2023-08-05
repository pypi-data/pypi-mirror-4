
from django.core.management.base import BaseCommand, CommandError

import os

from scss import Scss
css = Scss()

class Command(BaseCommand):
#    args = '<arg_x arg_y ...>'
    help = "Builds 'style.css' of markups in one css-file using pySCSS"

    def handle(self, *args, **options):
        my_path = os.path.dirname(__file__)
        sets_path = os.path.join(my_path, '../../static/markitup/sets/')
        sets_path = os.path.abspath(sets_path)

        style_scss = ''
        # sets list
        sets = [set_dir for set_dir in os.listdir(sets_path) if os.path.isdir(os.path.join(sets_path, set_dir))]
        for set_dir in sets:
            set_path = os.path.join(sets_path, set_dir, 'style.css')

            set_css = open(set_path, 'r').read()
            set_css = set_css.replace('url(images/', 'url({}/images/'.format(set_dir))

            set_scss = '.{set_dir} {{\n{set_css}\n}}\n'.format(set_dir=set_dir, set_css=set_css)

            style_scss += set_scss

        style_css = css.compile(style_scss)

        with open(os.path.join(sets_path, 'style.css'), 'w') as style_css_file:
            style_css_file.write(style_css)

#        style_css_file = open(os.path.join(sets_path, 'style.css'), 'w')
#        style_css_file.write(style_css)
#        style_css_file.close()

