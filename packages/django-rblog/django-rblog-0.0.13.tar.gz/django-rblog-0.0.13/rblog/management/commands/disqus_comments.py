from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings as conf
import rblog.models as mymodels

# Class MUST be named 'Command'
class Command(BaseCommand):

    # Displayed from 'manage.py help mycommand'
    help = "That's Your help message"

    # make_option requires options in optparse format
    option_list = BaseCommand.option_list  + (
                        make_option('--myoption', action='store',
                            dest='myoption',
                            default='default',
                            help='Option help message'),
                  )

    def handle(self, *app_labels, **options):
        """
        app_labels - app labels (eg. myapp in "manage.py reset myapp")
        options - configurable command line options
        """

        # Return a success message to display to the user on success
        # or raise a CommandError as a failure condition
        if options['myoption'] == 'default':
            if conf.DISQUS_SYNC:
                last_comment = mymodels.Comments.objects.all().order_by('-date')
                last_date_imported='2003-04-24 13:25:09'
                if last_comment:
                    last_date_imported=str(last_comment[0].date).replace('+00:00','')
                print last_date_imported
                try:
                    api = DisqusAPI(conf.DISQUS_API_SECRET, conf.DISQUS_API_PUBLIC)
                    for result in api.forums.listPosts(forum=conf.DISQUS_WEBSITE_SHORTNAME, limit='100', order='asc', since=last_date_imported):
                        if not mymodels.Comments.objects.filter(comment_id=result['id']):
                            newcomment = mymodels.Comments.objects.create(comment_id=result['id'], date=result['createdAt'].replace('T',' '))
                            newcomment.thread_id = result['thread']
                            newcomment.forum_id = conf.DISQUS_WEBSITE_SHORTNAME
                            newcomment.body = result['message']
                            newcomment.author_name = result['author']['name']
                            newcomment.author_url = result['author']['url']
                            newcomment.author_email = result['author']['emailHash']
                            newcomment.save()
                except:
                    pass
            return 'Success!'

        raise CommandError('Only the default is supported')