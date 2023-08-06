from django.core.management.base import LabelCommand
from BeautifulSoup import BeautifulSoup
import urllib2

class Command(LabelCommand):
    help = ("Outputs a stripped down version of the HTML from a given URL - removes all style, id's, classes and etc. Preserves HREF and name attributes only within tags.")
    args = "SOURCE_URL"
    label = 'source url'

    requires_model_validation = False
    can_import_settings = True

    def handle_label(self, label, **options):
        source_url = label
        keepers = {"href","name","src",}

        doc = urllib2.urlopen(source_url).read()
        soup = BeautifulSoup(doc)

        for tag in soup.body.findAll(True):
            tag.attrs[:] = [x for x in tag.attrs if x[0] in keepers]
        print soup.body.prettify()


def execute():
    """
    Helper function for running the command from the commandline directly
    """

    import argparse
    from django.conf import settings
    settings.configure()

    parser = argparse.ArgumentParser(description='Purify html (strip unwanted attributes and elements) from a given URL.')
    parser.add_argument('source_url',
        metavar='SOURCE_URL',
        type=str,
        help='Source URL to use for purifying',
    )

    args = parser.parse_args()

    cmd = Command()
    cmd.execute(args.source_url)
