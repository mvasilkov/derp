from django.conf import settings
from django.core.management.base import LabelCommand
from optparse import make_option
from tomoko.repaint.models import Point
from tomoko.repaint.picture import Canvas

class Command(LabelCommand):
    option_list = LabelCommand.option_list + (
        make_option('--size', type='int', default=0, dest='size'),
    )

    def handle_label(self, label, **options):
        size = options['size'] or settings.RE_SIZE
        canvas = Canvas(size, settings.RE_LEVEL)

        for v in xrange(size):
            for u in xrange(size):
                cons = tuple(canvas.cons_at(u, v))
                point = Point.objects.random_by_cons(cons)
                if point is None:
                    print 'I can haz moar data?'
                    canvas.save(label)
                    return
                canvas.paint(u, v, point.val)

        canvas.save(label)
