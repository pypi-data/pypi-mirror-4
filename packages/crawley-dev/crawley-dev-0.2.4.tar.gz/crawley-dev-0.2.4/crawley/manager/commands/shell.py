from crawley.crawlers import BaseCrawler
from crawley.extractors import XPathExtractor

from command import BaseCommand
from crawley.utils import exit_with_error


class ShellCommand(BaseCommand):
    """
        Shows an url data in a console like the XPathExtractor see it.
        So users can interactive scrape the data.
    """

    name = "shell"

    def validations(self):

        return [(len(self.args) >= 1, "No given url")]

    def execute(self):

        try:
            import IPython
        except ImportError:
            exit_with_error("Please install the ipython console")

        url = self.args[0]
        crawler = BaseCrawler()

        response = crawler._get_response(url)
        html = XPathExtractor().get_object(response)

        shell = IPython.Shell.IPShellEmbed(argv=[], user_ns={ 'response' : response })
        shell()
