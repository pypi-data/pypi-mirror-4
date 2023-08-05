======
README
======

  >>> from z3c.form.interfaces import IDataConverter

At least validate some components:

  >>> from m01.form.converter import MongoListTextLinesWidgetConverter
  >>> IDataConverter.implementedBy(MongoListTextLinesWidgetConverter)
  True

  >>> from m01.form.converter import MongoListMultiWidgetConverter
  >>> IDataConverter.implementedBy(MongoListMultiWidgetConverter)
  True

  >>> from m01.form.converter import MongoDatetimeConverter
  >>> IDataConverter.implementedBy(MongoDatetimeConverter)
  True
