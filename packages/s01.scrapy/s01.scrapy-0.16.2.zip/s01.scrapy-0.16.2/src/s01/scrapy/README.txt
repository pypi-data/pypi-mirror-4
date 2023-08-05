======
README
======

Item and Field
--------------

We use a different scrapy item and field concept then used in the scrapy
library. The concept uses well known zope pattern and offers hooks for
value convertion and serialization and also uses the zope.schema validation.

Note, our scapy item and field are not based on a dict.

  >>> import zope.interface
  >>> import zope.schema
  >>> import s01.scrapy.item
  >>> from s01.scrapy.fieldproperty import ScrapyFieldProperty

Let's define a scrapy item with some field properties but first define an
interface:

  >>> class ICar(zope.interface.Interface):
  ...     """Scrapy item describing a car"""
  ... 
  ...     color = zope.schema.TextLine(
  ...         title=u'Color',
  ...         default=u'',
  ...         required=True
  ...     )
  ... 
  ...     doors = zope.schema.Int(
  ...         title=u'Doors',
  ...         default=None,
  ...         required=False
  ...     )

We also define some converter which are able to convert given values:

  >>> def string2int(value):
  ...     if isinstance(value, list):
  ...         # try to find a value from a list of values
  ...         for v in value:
  ...             try:
  ...                 v = int(v)
  ...                 return v 
  ...             except ValueError, e:
  ...                 pass
  ...     else:
  ...         # try to convert a single value
  ...         try:
  ...             value = int(value)
  ...         except TypeError, e:
  ...             value = None
  ...     return value

  >>> def sequence2item(value):
  ...     if isinstance(value, list):
  ...         value = ' '.join(value)
  ...     return value

And a we can define a serializer which is able to transform given values to
something else. As a sample define a serializer which converts colors in 
known values:

  >>> def serializeColor(value):
  ...     if 'blue' in value:
  ...         return u'blue'
  ...     else:
  ...         return u'white'

  >>> class Car(s01.scrapy.item.ScrapyItemBase):
  ...     """Scrapy item describing a car"""
  ... 
  ...     zope.interface.implements(ICar)
  ... 
  ...     color = ScrapyFieldProperty(ICar['color'],
  ...                                 converter=sequence2item,
  ...                                 serializer=serializeColor)
  ...     doors = ScrapyFieldProperty(ICar['doors'],
  ...                                 converter=string2int)

Now let's setup an item and test our fields:

  >>> car = Car()
  >>> car.color = u'dark-blue'

As you can see the color get stored as is:

  >>> car.__dict__
  {'color': u'dark-blue'}

but if we get it as field value, the color get converted using our given
serializer:

  >>> car.color
  u'blue'

Since we use a sequence to item converter, we can also use a sequence as input
as valid input.

  >>> car = Car()
  >>> car.color = [u'light', u'blue']
  >>> car.color
  u'blue'

But we can't use a dict as input since our converter can't handle such values.
This means, we will run into a ValidationError which forces to raise a DropItem
error because the field is required:

  >>> car = Car()
  >>> car.color = {'color': u'blue'}
  Traceback (most recent call last):
  ...
  DropItem: ValidationError(({'color': u'blue'}, <type 'unicode'>, 'color')) for required field color:{'color': u'blue'}

Our new field converts values to an integer:

  >>> car = Car()
  >>> car.doors = u'4'
  >>> car.doors
  4

  >>> car = Car()
  >>> car.doors = [u'the car', u'has', u'5', u'doors']
  >>> car.doors
  5

But we can't use a dict as input since our converter can't handle such values.
This means, we will fallback to the default value since we run into a
ValidationError which get skiped because the field is NOT required.

  >>> car = Car()
  >>> car.doors = {'doors': u'6'}
  >>> car.doors is None
  True


dump
----

Our scrapy item also knows how to dump it's values. This dump method is used
in our custom scrapy item exporter.

  >>> car = Car()
  >>> car.color = u'blue'
  >>> car.doors = 5

  >>> car.color
  u'blue'

  >>> car.doors
  5

Now get the scrapy item data using our built-in dump method:

  >>> car.dump()
  {'color': u'blue', 'doors': 5}


order
-----

If order matters, you can sort the fields by it's interface order:

  >>> def getFieldNames(item):
  ...     fieldNames = []
  ...     for iface in zope.interface.providedBy(item):
  ...         for name in zope.schema.getFieldNamesInOrder(iface):
  ...             fieldNames.append(name)
  ...     return fieldNames

  >>> getFieldNames(car)
  ['color', 'doors']

  >>> def getOrderedValues(item):
  ...     values = []
  ...     for iface in zope.interface.providedBy(item):
  ...         for name in zope.schema.getFieldNamesInOrder(iface):
  ...             values.append(getattr(item, name))
  ...     return values

  >>> getOrderedValues(car)
  [u'blue', 5]
