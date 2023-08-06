# Custom Hamcrest Matchers

Highly reusable custom hamcrest matchers

## Installation

	python setup.py install

## Dependences

- lxml
- pyHamcrest


## Functions

- assert_that_raises


## Available matchers

-	empty
-	date_iso (ISO 8601 formatted date string)
- 	iterable
-	has_properties
-	has_keys
-	matches_re
-	callable_
-	json_
-   subset_of
-   superset_of 
-   disjoint_with

### xml matchers
-	xml_document
-	xml_root
-	xml_element
-	xml_contains_element
-	xml_namespaced
-	soap_document
-	soap_message


### assert_that_raises

```python
from hamcrest import *
from matchers import assert_that_raises

with assert_that_raises(Warning):
	raise Warning()

with assert_that_raises(instance_of(Warning)):
	raise Warning()

with assert_that_raises(has_property('message', has_string(u'warning'))):
	raise Warning(u'this is a warning')

# this raises AssertionError: no Exception raised
with assert_that_raises(NameError):
	raise Warning()

# {'exception': Warning(u'this is a warning')}
with assert_that_raises(Warning) as captured:
	raise Warning(u'this is a warning')

print captured['exception']
```

### empty

```python
from hamcrest import *
from matchers import empty

assert_that(str(), is_(empty()))
assert_that(set(), is_(empty()))
assert_that(dict(), is_(empty()))
assert_that(list(), is_(empty()))
assert_that(tuple(), is_(empty()))
assert_that(unicode(), is_(empty()))
```

It's smart enough to deal with iterators and generators

```python
assert_that(iter([]), is_(empty()))
assert_that((i for i in []), is_(empty()))
```

### date_iso (ISO 8601 formatted date string)

```python
from hamcrest import *
from matchers import date_iso

assert_that('1988-10-04T06:15:00.230943Z', is_(date_iso()))
```

### iterable

```python
from hamcrest import *
from matchers import iterable


assert_that(list(), is_(iterable()))
assert_that(dict(), is_(iterable()))
assert_that(tuple(), is_(iterable()))
assert_that(set(), is_(iterable()))

assert_that(str(), is_(iterable()))
assert_that(unicode(), is_(iterable()))

assert_that((i for i in []), is_(iterable()))
assert_that(iter([]), is_(iterable()))

class IterateMe(object):
	l = list()
	def __iter__(self):
		return iter(l)

assert_that(IterateMe(), is_(iterable()))
```

### has_properties

```python
from hamcrest import *
from matchers import has_properties

class Object(object):
	first = 'foo'
	second = 'bar'

assert_that(Object(), has_properties(first='foo', second='bar'))

assert_that(Object(), has_properties(dict(
		first='foo',
		second='bar'
})

assert_that(Object(), has_properties([
		('first', 'foo'), 
		('second', 'bar')
])
```

### has_keys

```python
from hamcrest import *
from matchers import has_keys

dictionary = {
	'first': 'foo',
	'second': 'bar'
}

assert_that(dictionary, has_keys(['first', 'second']))
```

### matches_re

```python
from hamcrest import *
from matchers import matches_re

assert_that('pattern', matches_re(r'pattern'))
```

### callable_

```python
from hamcrest import *
from matchers import callable_

assert_that(lambda : 'foo', is_(callable_()))
```

### json_

```python
from hamcrest import *
from matchers import json_

assert_that("{'foo': ['bar']}", is_(json_()))
assert_that("{'foo': ['bar']}", is_(json_(has_key('foo'))))
```

### subset_of

```python
from hamcrest import *
from matchers import subset_of

assert_that([1, 2], is_(subset_of([1, 2, 3])))
```

### superset_of

```python
from hamcrest import *
from matchers import superset_of

assert_that([1, 2, 3], is_(superset_of([1, 2])))
```

### disjoint_with

```python
from hamcrest import *
from matchers import disjoint_with

assert_that([1, 2, 3], is_(disjoint_with([4, 5, 6])))
```

### xml_document

```python
from hamcrest import *
from matchers import xml_document
from lxml.etree import _Element

assert_that('<element/>', is_(xml_document()))
assert_that('<element/>', is_(xml_document(instance_of(_Element))))
```

### xml_root

```python
from hamcrest import *
from matchers import xml_root
from lxml.etree import _Element

assert_that('<element/>', xml_root(tag='element'))
```

### xml_element

```python
from hamcrest import *
from matchers import xml_document, xml_element

assert_that('<element/>', is_(xml_element('element')))
assert_that('<element/>', is_(xml_element('element', another_matcher)))
assert_that('<foo:element/>', is_(xml_element(tag='element', ns='foo')))
```

### xml_contains_element

```python
from hamcrest import *
from matchers import xml_root, xml_element, xml_contains_element

assert_that('<parent><child/></parent>', 
	is_(xml_element('parent', xml_contains_element('child'))))

assert_that('<parent><child/></parent>', 
	xml_root(is_(xml_element('parent', xml_contains_element('child')))))
```

### xml_namespaced

```python
from hamcrest import *
from matchers import xml_namespaced

assert_that('<element xmlns="http://foo.com"/>',
	is_(xml_namespaced('http://foo.com')))
```

### soap_document

```python
from hamcrest import *
from matchers import xml_document, soap_document

ns_url = "http://schemas.xmlsoap.org/soap/envelope/"
string = "<Envelope xmlns='" + ns_url + "' />"

assert_that(string, is_(xml_document(is_(soap_document()))))
```

### soap_message

```python
from hamcrest import *
from matchers import xml_document, soap_document, soap_message

ns_url = "http://schemas.xmlsoap.org/soap/envelope/"
string = """
	<Envelope xmlns='""" + ns_url + """' >"
		<Body/>
	</Envelope>
"""

assert_that(string, 
		is_(xml_document(is_(soap_document(is_(soap_message()))))))
```
