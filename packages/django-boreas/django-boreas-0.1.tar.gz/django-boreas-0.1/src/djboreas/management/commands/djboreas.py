'''
Created on 14-03-2013

@author: karol
'''
from django.core.management.base import BaseCommand

import boreas.commands

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        boreas.commands.boreas()