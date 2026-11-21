from django.core.management.base import BaseCommand
from vl.models import Plugin
from pathlib import Path
from json import load as json_load


CUR_DIR = Path(__file__).parent


class Command(BaseCommand):
    help = "Register new plugin"

    def add_arguments(self, parser):
        parser.add_argument("plugin", nargs="+", type=str, help="The name of plugin")

    def handle(self, *args, **options):
        project_path = CUR_DIR.joinpath('..', '..', '..')
        for plugin_name in options['plugin']:
            plugin = Plugin.objects.filter(name=plugin_name).first()
            if not plugin:
                plugin = Plugin(name=plugin_name)
            with open(project_path.joinpath(plugin_name, 'declaration.json'), 'r') as plug_file:
                data = json_load(plug_file)
                plugin.one_click = data['one_click']
                plugin.double_click = data['double_click']
                plugin.record = data['record']
                plugin.rfid = data['rfid']
                plugin.cron = data['cron']
            plugin.save()
