__all__ = ('VERSION',)

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('django-debug-toolbar').version
except Exception, e:
    VERSION = 'unknown'

import datetime, itertools
from django.db import transaction
from django.db.models import Sum, Q
from django.utils.timezone import now
from collections import defaultdict
from monsieur.models import DataPoint, DataAttribute, Tag

@transaction.commit_on_success
def incr(name, amt, tag_names, *args, **kwargs):
    attrs = get_attrs(*args, **kwargs)

    data_attrs = []
    for key, val in attrs.items():
        id = DataAttribute.make(key, val)
        attr, created = DataAttribute.objects.get_or_create(key=key, value=val, id=id)
        data_attrs.append(attr)

    def get_tag(name):
        tag, _ = Tag.objects.get_or_create(name=name)
        return tag

    if isinstance(tag_names, str):
        tags = [get_tag(tag_names),]
    else:
        tags = [get_tag(name) for name in tag_names]

    dp = DataPoint.objects.create(
        name=name,
        count=amt,
        dt=this_minute(),
    )

    dp.attributes.add(*data_attrs)

    if tags:
        dp.tags.add(*tags)

    dp.save()

class Q(object):
    @classmethod
    def tag(cls, tag):
        qs = DataPoint.objects.filter(tags__name=tag)
        return Q(qs)

    @classmethod
    def events(cls, names):
        names = names if isinstance(names, list) else [names, ]
        qs = DataPoint.objects.filter(name__in=names)
        return Q(qs)

    def __init__(self, qs):
        self.qs = qs
        self.cached_results = None
        self._granularity = None

    def filter(self, *args, **kwargs):
        self.cached_results = None
        attrs = get_attrs(*args, **kwargs)
        pks = [DataAttribute.make(key, val) for key, val in attrs.items()]
        for key, val in attrs.items():
            if val == '*':
                self.qs = self.qs.filter(attributes__key=key)
                q_or = self.qs.filter(attributes__key=key)
            else:
                val = val.replace('\\*', '*')
                self.qs = self.qs.filter(attributes__pk=DataAttribute.make(key, val))

        return self

    def start(self, start):
        self.cached_results = None
        self.qs = self.qs.filter(dt__gte=start)
        return self

    def end(self, end):
        self.cached_results = None
        self.qs = self.qs.filter(dt__lte=end)
        return self

    def granularity(self, granularity):
        self.cached_results = None
        self._granularity = granularity
        return self

    def names(self):
        return [x['name'] for x in self.qs.values('name').annotate()]

    def attrs(self):
        xs = DataAttribute.objects.filter(points__in=self.qs).values('id').annotate()
        values = defaultdict(lambda: [])

        for row in xs:
            key, val = DataAttribute.split(row['id'])
            values[key].append(val)

        return dict(values)

    def eval(self):
        if not self.cached_results:
            raw_data = list(self.qs.values('name', 'dt').annotate(count=Sum('count')))
            data = defaultdict(lambda: [])
            for row in raw_data:
                data[row['name']].append({'dt': row['dt'], 'count': row['count']})

            for name in data.keys():
                data[name] = grouped(data[name], self._granularity)

            self.cached_results = data

        return self.cached_results

def grouped(data, granularity):
    rplc_args = {}
    if granularity in ['hour', 'day']:
        rplc_args.update({'minute': 0, 'second': 0, 'microsecond': 0})
    if granularity == 'day':
        rplc_args['hour'] = 0

    if len(rplc_args):
        grfn = lambda x: x['dt'].replace(**rplc_args)
        newdata = []
        for dt, pts in itertools.groupby(data, grfn):
            newdata.append({'dt': dt, 'count': sum(p['count'] for p in pts)})

        data = newdata

    return data



##################################################
# utils
def this_minute():
    return now().replace(
        second=0,
        microsecond=0
    )

def get_attrs(*args, **kwargs):
    attrs = {}
    if len(args) == 1:
        attrs = args[0]
        assert isinstance(attrs, dict)
    elif len(kwargs):
        attrs = dict(**kwargs)

    return attrs
