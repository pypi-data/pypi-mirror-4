from optparse import OptionParser

from command import BaseCommand
from crawley.manager.projects import project_types, CodeProject


class StartProjectCommand(BaseCommand):
    """
        Starts a new crawley project.

        Copies the files inside conf/project_template in order
        to generate a new project
    """

    name = "startproject"

    def __init__(self, args=None, project_type=None, project_name=None, base_dir=None):

        if args is None:
            args = []

        self.project_type = project_type
        self.base_dir = base_dir

        if project_type is not None:
            args.extend(["--type", project_type])

        if project_name is not None:
            args.append(project_name)

        BaseCommand.__init__(self, args)

    def validations(self):

        return [(len(self.args) >= 1, "No given project name")]

    def execute(self):

        self.parser = OptionParser()
        self.parser.add_option("-t", "--type", help="Type can be 'code' or 'template'")

        (options, args) = self.parser.parse_args(self.args)

        if options.type is None:

            options.type = CodeProject.name
            self.project_name = self.args[0]

        else:
            self.project_name = self.args[2]

        self.project_type = options.type

        project = project_types[self.project_type]()
        project.set_up(self.project_name, base_dir=self.base_dir)
