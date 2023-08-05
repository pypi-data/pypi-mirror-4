# -*- coding: utf-8 -*-
"""
General Command line tool

WARNING: Prototype
"""
import os, ConfigParser
from optparse import OptionValueError, make_option

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import CommandError, BaseCommand

import sveedocuments as SVEEROOT
from sveedocuments.local_settings import DOCUMENTS_CACHE_KEYS_TO_CLEAN
from sveedocuments.models import Page, Insert

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--clearcache", dest="clearcache", action="store_true", default=False, help="Clear all documents (Page and Insert) cache."),
        make_option("--make", dest="makemode", action="store_true", default=False, help="Make documents from ini file."),
        make_option("--config", dest="config_filepath", default=None, help="Filepath to ini file", metavar="FILEPATH"),
    )
    help = "General command for Sveetchies-documents"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        self.clearcache = options.get('clearcache')
        self.makemode = options.get('makemode')
        self.config_filepath = options.get('config_filepath')
        self.verbosity = int(options.get('verbosity'))
        
        if self.clearcache:
            self.do_clearcache()
        
        if self.makemode:
            self.do_make(self.config_filepath)

    def do_clearcache(self):
        """
        Clear all possible caches from documents
        """
        inserts = Insert.objects.all().order_by('id')
        for instance_item in inserts:
            keys = instance_item.clear_cache()
            
        pages = Page.objects.all().order_by('id')
        for page_item in pages:
            keys = page_item.clear_cache()
        
        if DOCUMENTS_CACHE_KEYS_TO_CLEAN:
            cache.delete_many(DOCUMENTS_CACHE_KEYS_TO_CLEAN)
            
        if self.verbosity:
            print "* All documents cache cleared"

    def do_make(self, config):
        print "Dummy make !"
        print self._get_config()
    
    def _get_config(self):
        """
        Retrieves the configuration

        Tries to get the configuration from an *.ini style file
        
        :rtype: object `ConfigParser.SafeConfigParser`
        :return: Object containing user's configuration.
        """
        sveeroot = os.path.abspath(os.path.dirname(SVEEROOT.__file__))
        cfname = os.path.join(sveeroot, 'export_config.ini')
        
        conf = ConfigParser.SafeConfigParser({})
        conf.read([cfname])
        return conf
