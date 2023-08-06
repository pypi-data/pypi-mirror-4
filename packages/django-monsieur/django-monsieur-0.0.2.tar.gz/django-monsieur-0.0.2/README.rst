====================
django-monsieur
====================

monsieur is a Django app designed to track/monitor/query arbitrary
events over periods of time.

====================
Usage
====================

Once installed (instructions below), simply import monsieur and start
logging events.

::

  # views.py
  import monsieur

  def handler(request):
      try:
          handle_request(request)
      except Exception as e:
          # log exception to monsieur and add os/browser attributes
          os, browser = parse_ua(request.META.get('HTTP_USER_AGENT'))
          name = e.message or 'Unknown exception in handler()'
          monsieur.incr(name, 1, 'view errors', os=os, browser=browser)


monsieur has a query system similar to Django's querysets::

  >>> import monsieur
  >>> q = monsieur.Q.tag('view errors')
  >>> q = q.filter(os='windows')
  >>> q = q.granularity('hour')
  >>> q.eval()
  {'integer division or modulo by zero': [{'dt': datetime.datetime(2013, 1, 7, 20, 0, 0, 0), 'count': 1}, ...]}


--------------------
Q constructors
--------------------

::
  
  Q.tag(x)        # x = TAG | [TAG1, TAG2, ...]

  Q.events(x)     # x = NAME | [NAME1, NAME2, ...]


--------------------
Q methods
--------------------

::

  q.filter(**kwargs)   # key=value to filter by
  
  q.start(x)           # x = datetime.datetime 
  
  q.end(x)             # x = datetime.datetime
  
  q.granularity(x)     # x = 'minute' | 'hour' | 'day'


--------------------
Q evaluation methods
--------------------

::

  q.names()

  q.eval()

