What is Rx?
===========

When adding an API to your web service, you have to choose how to encode the
data you send across the line. XML is one common choice for this, but it can
grow arcane and cumbersome pretty quickly. Lots of webservice authors want to
avoid thinking about XML, and instead choose formats that provide a few simple
data types that correspond to common data structures in modern programming
languages. In other words, JSON and YAML.

Unfortunately, while these formats make it easy to pass around complex data
structures, they lack a system for validation. XML has XML Schemas and RELAX
NG, but these are complicated and sometimes confusing standards. They're not
very portable to the kind of data structure provided by JSON, and if you wanted
to avoid XML as a data encoding, writing more XML to validate the first XML is
probably even less appealing.

Rx is meant to provide a system for data validation that matches up with
JSON-style data structures and is as easy to work with as JSON itself.

rxjson
======

rxjson is a python package that helps you validate your generated JSON
against a standardized json schema directly in your python app.

It is a packaged version of http://rx.codesimply.com/

Usage
=====

Here is a little example of how to validate your json against a rx schema::

    import requests
    from rxjson import Rx
    import unittest
    
    class SporeTest(unittest.TestCase):
        """Test generate spore schema."""
        def test_spore(self):
            rx = Rx.Factory({ "register_core_types": True })
			with open('spore_validation.rx') as f:
                spore_json_schema = json.loads(f.read())
                spore_schema = rx.make_schema(spore_json_schema)
                resp = requests.get('http://localhost:8000/spore', headers={'Content-Type': 'application/json'})
                self.assertTrue(spore_schema.check(resp.json))

Or even quicker::

    >>> import json
    >>> from rxjson import Rx
    >>> rx = Rx.Factory({ "register_core_types": True })
    >>> spore_json_schema = json.loads(open('spore_validation.rx').read())
    >>> spore_schema = rx.make_schema(spore_json_schema)
    >>> js = json.loads("""{
    ...     "base_url": "http://localhost:8000",
    ...     "expected_status": [200],
    ...     "version": "0.1",
    ...     "methods": {
    ...         "put_data_item": {
    ...             "path": "/data/:model_name/:data_item_id",
    ...             "description": "Update a data item.",
    ...             "required_params": ["model_name", "data_item_id"],
    ...             "method": "PUT",
    ...             "formats": ["json"]
    ...         }
    ...     },
    ...     "name": "daybed"
    ... }""")
    >>> spore_schema.check(js)
    True

* ``spore_validation.rx`` is part of https://github.com/SPORE/specifications
* ``daybed`` is a form model validation API: https://github.com/spiral-project/daybed
