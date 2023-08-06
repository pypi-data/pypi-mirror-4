import sys
import os
from optparse import OptionParser

from crawley.utils import exit_with_error, import_user_module, check_for_file, fix_file_extension, has_valid_attr, add_to_path
from crawley.manager.projects import project_types


class BaseCommand(object):
    """
        Base Crawley's Command
    """

    name = "BaseCommand"

    def __init__(self, args):

        self.args = args

    def check_validations(self):
        """
            Checks for validations
        """

        for validation, message in self.validations():
            if not validation:
                exit_with_error(message)

    def validations(self):
        """
            Returns a list of tuples containing:
                [(validate_condition, error_message)]
        """

        return []

    def execute(self):
        """
            Executes the command
        """

        raise NotImplementedError()

    def checked_execute(self):
        """
            Checks before Execute
        """

        self.check_validations()
        self.execute()


class ProjectCommand(BaseCommand):
    """
        A command that requires a settings.py file to run
    """

    def __init__(self, args=None, settings=None, **kwargs):

        self.kwargs = kwargs
        self.settings = settings

        BaseCommand.__init__(self, args)

    def checked_execute(self):
        """
            Checks for settings before run
        """

        if self.settings is None:
            self._add_options()
            self.settings = self._check_for_settings()
        else:
            add_to_path(self.settings.PROJECT_ROOT)

        self._check_settings_errors()
        self._check_project_type()
        BaseCommand.checked_execute(self)

    def _add_options(self):
        """
            Add options that can be procesed by OptionParser
        """

        self.parser = OptionParser()
        self.parser.add_option("-s", "--settings", help="Indicates the settings.py file")

    def _check_for_settings(self):
        """
            tries to import the user's settings file
        """

        (options, args) = self.parser.parse_args(self.args)

        if options.settings is not None:

            settings_dir, file_name = os.path.split(options.settings)

            add_to_path(settings_dir)
            settings_file = os.path.splitext(file_name)[0]

        else:
            add_to_path(os.getcwd())
            settings_file = "settings"

        settings = import_user_module(settings_file)

        add_to_path(settings.PROJECT_ROOT)
        return settings

    def _check_settings_errors(self):
        """
            Fix errors in settings.py
        """

        if hasattr(self.settings, 'DATABASE_ENGINE'):
            if self.settings.DATABASE_ENGINE == 'sqlite':
                self.settings.DATABASE_NAME = fix_file_extension(self.settings.DATABASE_NAME, 'sqlite')

        if hasattr(self.settings, 'JSON_DOCUMENT'):
            self.settings.JSON_DOCUMENT = fix_file_extension(self.settings.JSON_DOCUMENT, 'json')

        if hasattr(self.settings, 'XML_DOCUMENT'):
            self.settings.XML_DOCUMENT = fix_file_extension(self.settings.XML_DOCUMENT, 'xml')

    def _check_project_type(self):
        """
            Check for the project's type
        """

        if has_valid_attr(self.settings, "PROJECT_TYPE"):
            project_type = self.settings.PROJECT_TYPE
        else:
            meta_data = import_user_module("__init__")
            project_type = meta_data.project_type

        self.project_type = project_types[project_type]()
