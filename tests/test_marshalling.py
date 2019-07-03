# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from sanic_restplus import (
    marshal,
    marshal_with,
    marshal_with_field,
    fields,
    Api,
    Resource,
)

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


# Add a dummy Resource to verify that the app is properly set.
class HelloWorld(Resource):
    def get(self):
        return {}


class MarshallingTest(object):
    def test_marshal(self):
        model = OrderedDict([("foo", fields.Raw)])
        marshal_dict = OrderedDict([("foo", "bar"), ("bat", "baz")])
        output = marshal(marshal_dict, model)
        assert output == {"foo": "bar"}

    def test_marshal_with_envelope(self):
        model = OrderedDict([("foo", fields.Raw)])
        marshal_dict = OrderedDict([("foo", "bar"), ("bat", "baz")])
        output = marshal(marshal_dict, model, envelope="hey")
        assert output == {"hey": {"foo": "bar"}}

    def test_marshal_with_skip_none(self):
        model = OrderedDict(
            [("foo", fields.Raw), ("bat", fields.Raw), ("qux", fields.Raw)]
        )
        marshal_dict = OrderedDict([("foo", "bar"), ("bat", None)])
        output = marshal(marshal_dict, model, skip_none=True)
        assert output == {"foo": "bar"}

    async def test_marshal_decorator(self):
        model = OrderedDict([("foo", fields.Raw)])

        @marshal_with(model)
        def try_me(request):
            return OrderedDict([("foo", "bar"), ("bat", "baz")])

        assert await try_me(None) == {"foo": "bar"}

    async def test_marshal_decorator_with_envelope(self):
        model = OrderedDict([("foo", fields.Raw)])

        @marshal_with(model, envelope="hey")
        def try_me(request):
            return OrderedDict([("foo", "bar"), ("bat", "baz")])

        assert await try_me(None) == {"hey": {"foo": "bar"}}

    async def test_marshal_decorator_with_skip_none(self):
        model = OrderedDict(
            [("foo", fields.Raw), ("bat", fields.Raw), ("qux", fields.Raw)]
        )

        @marshal_with(model, skip_none=True)
        def try_me(request):
            return OrderedDict([("foo", "bar"), ("bat", None)])

        assert await try_me(None) == {"foo": "bar"}

    async def test_marshal_decorator_tuple(self):
        model = OrderedDict([("foo", fields.Raw)])

        @marshal_with(model)
        def try_me(request):
            headers = {"X-test": 123}
            return OrderedDict([("foo", "bar"), ("bat", "baz")]), 200, headers

        assert await try_me(None) == ({"foo": "bar"}, 200, {"X-test": 123})

    async def test_marshal_decorator_tuple_with_envelope(self):
        model = OrderedDict([("foo", fields.Raw)])

        @marshal_with(model, envelope="hey")
        def try_me(request):
            headers = {"X-test": 123}
            return OrderedDict([("foo", "bar"), ("bat", "baz")]), 200, headers

        assert await try_me(None) == ({"hey": {"foo": "bar"}}, 200, {"X-test": 123})

    async def test_marshal_decorator_tuple_with_skip_none(self):
        model = OrderedDict(
            [("foo", fields.Raw), ("bat", fields.Raw), ("qux", fields.Raw)]
        )

        @marshal_with(model, skip_none=True)
        def try_me(request):
            headers = {"X-test": 123}
            return OrderedDict([("foo", "bar"), ("bat", None)]), 200, headers

        assert await try_me(None) == ({"foo": "bar"}, 200, {"X-test": 123})

    async def test_marshal_field_decorator(self):
        model = fields.Raw

        @marshal_with_field(model)
        def try_me(request):
            return "foo"

        assert await try_me(None) == "foo"

    async def test_marshal_field_decorator_tuple(self):
        model = fields.Raw

        @marshal_with_field(model)
        def try_me(request):
            return "foo", 200, {"X-test": 123}

        assert await try_me(None) == ("foo", 200, {"X-test": 123})

    def test_marshal_field(self):
        model = OrderedDict({"foo": fields.Raw()})
        marshal_fields = OrderedDict([("foo", "bar"), ("bat", "baz")])
        output = marshal(marshal_fields, model)
        assert output == {"foo": "bar"}

    def test_marshal_tuple(self):
        model = OrderedDict({"foo": fields.Raw})
        marshal_fields = OrderedDict([("foo", "bar"), ("bat", "baz")])
        output = marshal((marshal_fields,), model)
        assert output == [{"foo": "bar"}]

    def test_marshal_tuple_with_envelope(self):
        model = OrderedDict({"foo": fields.Raw})
        marshal_fields = OrderedDict([("foo", "bar"), ("bat", "baz")])
        output = marshal((marshal_fields,), model, envelope="hey")
        assert output == {"hey": [{"foo": "bar"}]}

    def test_marshal_tuple_with_skip_none(self):
        model = OrderedDict(
            [("foo", fields.Raw), ("bat", fields.Raw), ("qux", fields.Raw)]
        )
        marshal_fields = OrderedDict([("foo", "bar"), ("bat", None)])
        output = marshal((marshal_fields,), model, skip_none=True)
        assert output == [{"foo": "bar"}]

    def test_marshal_nested(self):
        model = OrderedDict(
            [("foo", fields.Raw), ("fee", fields.Nested({"fye": fields.String}))]
        )

        marshal_fields = OrderedDict(
            [("foo", "bar"), ("bat", "baz"), ("fee", {"fye": "fum"})]
        )
        output = marshal(marshal_fields, model)
        expected = OrderedDict([("foo", "bar"), ("fee", OrderedDict([("fye", "fum")]))])
        assert output == expected

    def test_marshal_nested_with_non_null(self):
        model = OrderedDict(
            [
                ("foo", fields.Raw),
                (
                    "fee",
                    fields.Nested(
                        OrderedDict([("fye", fields.String), ("blah", fields.String)]),
                        allow_null=False,
                    ),
                ),
            ]
        )
        marshal_fields = [OrderedDict([("foo", "bar"), ("bat", "baz"), ("fee", None)])]
        output = marshal(marshal_fields, model)
        expected = [
            OrderedDict(
                [("foo", "bar"), ("fee", OrderedDict([("fye", None), ("blah", None)]))]
            )
        ]
        assert output == expected

    def test_marshal_nested_with_null(self):
        model = OrderedDict(
            [
                ("foo", fields.Raw),
                (
                    "fee",
                    fields.Nested(
                        OrderedDict([("fye", fields.String), ("blah", fields.String)]),
                        allow_null=True,
                    ),
                ),
            ]
        )
        marshal_fields = OrderedDict([("foo", "bar"), ("bat", "baz"), ("fee", None)])
        output = marshal(marshal_fields, model)
        expected = OrderedDict([("foo", "bar"), ("fee", None)])
        assert output == expected

    def test_marshal_nested_with_skip_none(self):
        model = OrderedDict(
            [
                ("foo", fields.Raw),
                (
                    "fee",
                    fields.Nested(
                        OrderedDict([("fye", fields.String)]), skip_none=True
                    ),
                ),
            ]
        )
        marshal_fields = OrderedDict([("foo", "bar"), ("bat", "baz"), ("fee", None)])
        output = marshal(marshal_fields, model, skip_none=True)
        expected = OrderedDict([("foo", "bar")])
        assert output == expected

    def test_allow_null_presents_data(self):
        model = OrderedDict(
            [
                ("foo", fields.Raw),
                (
                    "fee",
                    fields.Nested(
                        OrderedDict([("fye", fields.String), ("blah", fields.String)]),
                        allow_null=True,
                    ),
                ),
            ]
        )
        marshal_fields = OrderedDict(
            [("foo", "bar"), ("bat", "baz"), ("fee", {"blah": "cool"})]
        )
        output = marshal(marshal_fields, model)
        expected = OrderedDict(
            [("foo", "bar"), ("fee", OrderedDict([("fye", None), ("blah", "cool")]))]
        )
        assert output == expected

    def test_skip_none_presents_data(self):
        model = OrderedDict(
            [
                ("foo", fields.Raw),
                (
                    "fee",
                    fields.Nested(
                        OrderedDict(
                            [
                                ("fye", fields.String),
                                ("blah", fields.String),
                                ("foe", fields.String),
                            ]
                        ),
                        skip_none=True,
                    ),
                ),
            ]
        )
        marshal_fields = OrderedDict(
            [("foo", "bar"), ("bat", "baz"), ("fee", {"blah": "cool", "foe": None})]
        )
        output = marshal(marshal_fields, model)
        expected = OrderedDict(
            [("foo", "bar"), ("fee", OrderedDict([("blah", "cool")]))]
        )
        assert output == expected

    def test_marshal_nested_property(self):
        class TestObject(object):
            @property
            def fee(self):
                return {"blah": "cool"}

        model = OrderedDict(
            [
                ("foo", fields.Raw),
                (
                    "fee",
                    fields.Nested(
                        OrderedDict([("fye", fields.String), ("blah", fields.String)]),
                        allow_null=True,
                    ),
                ),
            ]
        )
        obj = TestObject()
        obj.foo = "bar"
        obj.bat = "baz"
        output = marshal([obj], model)
        expected = [
            OrderedDict(
                [
                    ("foo", "bar"),
                    ("fee", OrderedDict([("fye", None), ("blah", "cool")])),
                ]
            )
        ]
        assert output == expected

    def test_marshal_nested_property_with_skip_none(self):
        class TestObject(object):
            @property
            def fee(self):
                return {"blah": "cool", "foe": None}

        model = OrderedDict(
            [
                ("foo", fields.Raw),
                (
                    "fee",
                    fields.Nested(
                        OrderedDict(
                            [
                                ("fye", fields.String),
                                ("blah", fields.String),
                                ("foe", fields.String),
                            ]
                        ),
                        skip_none=True,
                    ),
                ),
            ]
        )
        obj = TestObject()
        obj.foo = "bar"
        obj.bat = "baz"
        output = marshal([obj], model)
        expected = [
            OrderedDict([("foo", "bar"), ("fee", OrderedDict([("blah", "cool")]))])
        ]
        assert output == expected

    def test_marshal_list(self):
        model = OrderedDict([("foo", fields.Raw), ("fee", fields.List(fields.String))])
        marshal_fields = OrderedDict(
            [("foo", "bar"), ("bat", "baz"), ("fee", ["fye", "fum"])]
        )
        output = marshal(marshal_fields, model)
        expected = OrderedDict([("foo", "bar"), ("fee", (["fye", "fum"]))])
        assert output == expected

    def test_marshal_list_of_nesteds(self):
        model = OrderedDict(
            [
                ("foo", fields.Raw),
                ("fee", fields.List(fields.Nested({"fye": fields.String}))),
            ]
        )
        marshal_fields = OrderedDict(
            [("foo", "bar"), ("bat", "baz"), ("fee", {"fye": "fum"})]
        )
        output = marshal(marshal_fields, model)
        expected = OrderedDict(
            [("foo", "bar"), ("fee", [OrderedDict([("fye", "fum")])])]
        )
        assert output == expected

    def test_marshal_list_of_lists(self):
        model = OrderedDict(
            [("foo", fields.Raw), ("fee", fields.List(fields.List(fields.String)))]
        )
        marshal_fields = OrderedDict(
            [("foo", "bar"), ("bat", "baz"), ("fee", [["fye"], ["fum"]])]
        )
        output = marshal(marshal_fields, model)
        expected = OrderedDict([("foo", "bar"), ("fee", [["fye"], ["fum"]])])
        assert output == expected

    def test_marshal_nested_dict(self):
        model = OrderedDict(
            [
                ("foo", fields.Raw),
                ("bar", OrderedDict([("a", fields.Raw), ("b", fields.Raw)])),
            ]
        )
        marshal_fields = OrderedDict(
            [
                ("foo", "foo-val"),
                ("bar", "bar-val"),
                ("bat", "bat-val"),
                ("a", 1),
                ("b", 2),
                ("c", 3),
            ]
        )
        output = marshal(marshal_fields, model)
        expected = OrderedDict(
            [("foo", "foo-val"), ("bar", OrderedDict([("a", 1), ("b", 2)]))]
        )
        assert output == expected

    @pytest.mark.options(debug=True)
    async def test_will_prettyprint_json_in_debug_mode(self, app, client):
        api = Api()

        class Foo1(Resource):
            def get(self, request):
                return {"foo": "bar", "baz": "asdf"}

        api.add_resource(Foo1, "/foo", endpoint="bar")

        app.restplus_plugin.api(api)
        foo = await client.get("/foo")

        # Python's dictionaries have random order (as of "new" Pythons,
        # anyway), so we can't verify the actual output here.  We just
        # assert that they're properly prettyprinted.
        data = await foo.text()
        assert '"foo":"bar"' in data
        assert '"baz":"asdf"' in data
        assert data.strip().startswith('{"')
        assert data.strip().endswith('"}')

    async def test_json_float_marshalled(self, app, client):
        api = Api()

        class FooResource(Resource):
            fields = {"foo": fields.Float}

            def get(self, request):
                return marshal({"foo": 3.0}, self.fields)

        api.add_resource(FooResource, "/api")

        app.restplus_plugin.api(api)
        resp = await client.get("/api")
        assert resp.status == 200
        assert await resp.text() == '{"foo":3.0}\n'
