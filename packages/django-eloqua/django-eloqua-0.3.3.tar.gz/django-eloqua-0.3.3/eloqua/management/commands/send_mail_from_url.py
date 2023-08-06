from django.core.management.base import BaseCommand, CommandError
from datetime import date
from time import sleep
from django.conf import settings
import requests
from eloqua.clients import EloquaClient
from optparse import make_option

subjectOption = make_option('--subject',
    action='store',
    dest='subject',
    default=None,
    help='Set the subject for the mail')

nameOption = make_option('--name',
    action='store',
    dest='name',
    default=None,
    help='Set the name for this mail')

urlOption = make_option('--url',
    action='store',
    dest='url',
    default=None,
    help='Sets the url to fetch as base for this mailing')

fromNameOption = make_option('--from-name',
    action='store',
    dest='from_name',
    default=None,
    help='Sets the reply-to name for the mail')

fromEmailOption = make_option('--from-email',
    action='store',
    dest='from_email',
    default=None,
    help='Sets the reply-to email for the mail')


class Command(BaseCommand):
    help = 'Create mail in Eloqua, based of a url (eg: newsletters)'
    option_list = BaseCommand.option_list + (subjectOption, nameOption, urlOption, fromEmailOption, fromNameOption)

    def handle(self, *args, **options):
        if 'url' not in options:
            raise CommandError('We need a URL to base from')

        try:
            response = requests.get(options['url'])
        except:
            raise CommandError('Could not fetch url')

        e = EloquaClient()
        body = response.content

        # get the subject from the title, if none given
        if options['subject'] is None:
            from BeautifulSoup import BeautifulSoup
            soup = BeautifulSoup(body)
            options['subject'] = soup.title.string

        # if no name is given, set the name the same as the subject
        if options['name'] is None:
            options['name'] = options['subject']

        print e.emails.create(options['name'], options['subject'], body, reply_to_name=options['from_name'], reply_to_email=options['from_email'])
