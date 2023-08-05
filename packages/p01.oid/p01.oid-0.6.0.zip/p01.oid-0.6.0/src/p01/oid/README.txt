======
README
======

In default zope 3 projects, we use an IntIds utility for reference objects.
This is an overhead and has different negativ aspects for applications which
will need high performance. The IIntIds utility will allways allocate keys and
store the objects with this keys if we register new objects.

We already have such keys stored in each persistent objects.
(Well in case the project uses ZODB for storage)

This package offers access to the _p_oid assigned for each object as an object
ID which can get used as a replacement for the IntIds utility given unique ID.
The database already makes sure that this ID is unique.

Another benefit from this concept is that we never reuse such a unique id which
is not true for the current IIntIds utility implementation. Think about what
could happen if you reference objects by their unique IIntIds and an object
gets removed and a new (unique) IIntIds utility id gets applied to another object.
If you don't remove any object reference everywhere, then a wrong object will get
referenced. This means if you use the IIntIds concept and you will reference
objects by their IIntIds utility id, you must remove all references if an object
gets removed. This is a no go in our applications because of speedup reasons.

Our implementation provides an adapter instead of an utility. This adapter is
able to handle objects and their ids. Note, we only make existing object ids
available, we never change them.

The p01.oid concept provides the following benefits:

- never generates write conflicts because we never store something

- only depends on the Persistent class and a database connection

As you can see the p01.oid concept is not just a replacement. It's more a
base concept for your development strategie.

Since this package is conflict free and provides a great speedup, you will find
them in many of our packages.

Just another hint which is not really relevant for our impelentation but
probably interesing if you're looking for more speedup. Check if your objects
are independent from other objects and if so implement _p_independent. This
will eleminate read conflict errors. For more information check the interface
IPersistentNoReadConflicts in the persistent package.

Note, we do not explicitely check IOIDAware in our getter and setter methods
because of speedup reason. It's up to the application only to activate the oid
for valid objects.

  >>> import ZODB.tests.util
  >>> import transaction
  >>> import zope.component
  >>> import zope.event
  >>> import zope.lifecycleevent.interfaces
  >>> from zope.component import hooks
  >>> from zope.site import LocalSiteManager
  >>> import p01.oid.api
  >>> import p01.oid.oid
  >>> from p01.oid import interfaces
  >>> from p01.oid import testing

Let's first setup a database:

  >>> databases = {}
  >>> db = ZODB.tests.util.DB(databases=databases, database_name='db')

 and a connection:

  >>> tm = transaction.TransactionManager()
  >>> conn = db.open(transaction_manager=tm)

Now setup a site:

  >>> site = testing.MySite()

  >>> sm = LocalSiteManager(site)
  >>> site.setSiteManager(sm)

Set the site as the current site. This is normaly done by traversing to a
site:

  >>> hooks.setSite(site)

Now add the site to the database:

  >>> root = conn.root()
  >>> root['site'] = site
  >>> tm.commit()

Now we can setup our OIDAware object:

  >>> obj = testing.MyObject(u'MyObject')
  >>> interfaces.IOIDAware.providedBy(obj)
  True

As you can see, we do not have an oid or _p_oid available. This means the
object get not added to the database connection:

  >>> obj._p_oid is None
  True


Let's add the object to the connection and apply an _p_oid:

  >>> conn._added
  {}

  >>> p01.oid.api.addObject(obj)
  15

As you can see the object has a _p_oid now and is added to the connection and
provides an oid value based on the given _p_oid:

  >>> conn._added
  {'\x00\x00\x00\x00\x00\x00\x00\x0f': <MyObject MyObject>}

  >>> obj.oid
  15

The type of the oid is ``int``:

  >>> type(obj.oid)
  <type 'int'>


getObject
---------

We also provide some methods which allow us to handle objects based on their
oid:

  >>> back = p01.oid.api.getObject(obj.oid)
  >>> back
  <MyObject MyObject>

This must be the same as the original object:

  >>> obj is back
  True


queryObject
-----------

The queryObject method does the same like the getObject method but will return
the given default value if an object is not available:

  >>> p01.oid.api.queryObject(obj.oid)
  <MyObject MyObject>

If we query for an object which is not available, we will not run into a
KeyError like we do with getObject:

  >>> p01.oid.api.getObject(42)
  Traceback (most recent call last):
  ...
  KeyError: 42

  >>> p01.oid.api.queryObject(42) is None
  True


yieldObjects
------------

The yieldObjects method is able to yield objects for the given list of oids:

  >>> p01.oid.api.yieldObjects([1, 2, 3, 42])
  <generator object ...>

As you can see, we will get a generator objects which we can iterate. If we
iterate, we will only get available objects. As you can see the object with
the oid 15 is the only one we will get bacause all other objects fo not
provide an oid attribute:

  >>> tuple(p01.oid.api.yieldObjects([1, 14, 15, 42]))
  (<MyObject MyObject>,)


connections
-----------

Let's open a new connection and check the object we stored before. But first
commit the trnsaction and close the connection:

  >>> tm.commit()
  >>> conn.close()

  >>> tm2 = transaction.TransactionManager()
  >>> conn = db.open(transaction_manager=tm)
  >>> p01.oid.api.getObject(obj.oid)
  <MyObject MyObject>


IOIDManager
-----------

Our IOIDManager adapter allows to lookup objects and their object ids. The
adapter must adapt a persistent object which is stored in the same database
as the object or id we like to lookup. During adaption the adapter will get
a connection based on the object we adapt. First register our adapter:

  >>> zope.component.provideAdapter(p01.oid.oid.OIDManager)

Let's adapt our site:

  >>> oids = interfaces.IOIDManager(site)
  >>> oids
  <OIDManager for <MySite>>

Let's get our sample object again from the adapter by it's oid:

  >>> obj == oids.getObject(obj.oid)
  True

Or get the oid based on our object. Of corse this is what obj.oid returns:

  >>> obj.oid == oids.getOID(obj)
  True

You can think this is not usefull but wait this method will get an oid for a
new object which does not have one yet:

  >>> new = testing.MyObject(u'New Object')

such a new object does not have a connection or an object id yet:

  >>> new._p_jar is None
  True

  >>> new._p_oid is None
  True

The adapter also provides an add method which we can use for add an oid:

  >>> oids.add(new)
  16

  >>> new.oid
  16

As you can see the add method added the object and returns the new
added oid. We can get such an oid also within the adapters getOID method:

  >>> oids.getOID(new)
  16

Our adapter can also query an oid:

  >>> another = testing.MyObject(u'New Object')
  >>> oids.queryOID(new)
  16

if we query for a not added object, we will get None as result:

  >>> another = testing.MyObject(u'New Object')
  >>> another._p_jar is None
  True

  >>> another._p_oid is None
  True

  >>> oids.queryOID(another) is None
  True


we can also query an object for an non existing oid. This will not raise an
error like the getObject method does:

  >>> oids.getObject(17)
  Traceback (most recent call last):
  ...
  KeyError: 17

  >>> oids.queryObject(17) is None
  True


Edge case
---------

Is it possible that if we remove an object in our application but this does not
really remove the object from the database. The object is still available in
our database. Our implementation will ensure that we only return objects
which we actived by apply the _oid value. Let's test this:

  >>> missing = testing.MyObject(u'Missing Object')
  >>> p01.oid.api.addObject(missing)
  17
  >>> site['missing'] = missing
  >>> tm.commit()

let's get them by it's oid. Do this by using the low level API which our concept
is based on e.g. use a connection:

  >>> _p_oid = missing._p_oid
  >>> conn.get(_p_oid)
  <MyObject Missing Object>

  >>> oid = missing.oid
  >>> p01.oid.api.getObject(oid)
  <MyObject Missing Object>

Now remove the object:

  >>> del site['missing']
  >>> tm.commit()

As you can see the object is not available in our site:

  >>> site.get('missing') is None
  True

But the object is still available in our connection:

  >>> conn.get(_p_oid)
  <MyObject Missing Object>

And our API will also return such objects.

  >>> p01.oid.api.getObject(oid)
  <MyObject Missing Object>

This is really not what we need. The test below explains how we handle this.


Event subscriber
----------------

The event subscriber concept will ensure that we apply and remove the oid
on objects if we notify object created and object remove events. Let's use a
new object:

  >>> obj = testing.MyObject(u'Event Object')

Now we can just notify an object created event which will dispatch the event to
our add event handler. We do this here without a complex event handler setup:

  >>> from p01.oid import event
  >>> added = zope.lifecycleevent.ObjectCreatedEvent(obj)
  >>> event.addOIDSubscriber(obj, added)

As you can see we now have an oid:

  >>> oid = obj.oid
  >>> oid
  19

Now we can get the object within our API

  >>> p01.oid.api.getObject(oid)
  <MyObject Event Object>

or within our adapter:

  >>> oids.getObject(oid)
  <MyObject Event Object>


Our other event subscriber is able to remove the oid from an object. This
subscriber is registered as an ObjectRemovedEvent subscriber:

  >>> removed = zope.lifecycleevent.ObjectRemovedEvent(obj)
  >>> event.removeOIDSubscriber(obj, removed)

As you can see the oid get set to None:

  >>> obj.oid is None
  True

and we can not access the object within our API or adapter:


  >>> p01.oid.api.getObject(oid)
  Traceback (most recent call last):
  ...
  KeyError: 19

  >>> oids.getObject(oid)
  Traceback (most recent call last):
  ...
  KeyError: 19
