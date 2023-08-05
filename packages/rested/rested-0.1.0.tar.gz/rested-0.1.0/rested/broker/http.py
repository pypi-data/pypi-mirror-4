from rested.broker import Broker
from rested.action import ACTION_TYPES

__all__ = ["HttpBroker"]


class HttpBroker(Broker):
    # Map to determine type of http request.
    #   method, body?
    #
    # any extra parameters if body is not included will be encoded as request
    # uri
    # parameters.
    method_map = {
        "read": ("GET", False),
        "write": ("POST", True),
        "update": ("PUT", True),
        "delete": ("DELETE", False)
    }

    def __init__(self, impl):
        self.impl = impl

    def _yield_uri_parts(self, ns, path, action):
        if action.action_type not in ACTION_TYPES:
            raise RuntimeError(
                "Unsupported action type '{0}'".format(
                    action.action_type))

        def check_yield_single(ns, entity):
            """
            Check that the specified entity value is in namespace and yield
            a parameterized uri part.
            """
            value = getattr(ns, entity.singular, None)

            if value is None:
                raise RuntimeError(
                    "Missing argument '{0}' in namespace {1}".format(
                        entity.singular,
                        ns))

            delattr(ns, entity.singular)

            yield "{0}/{1}".format(entity.plural, value)

        # build prefix uri depending on the path taken
        # these are all assumed to be of action type 'single'.
        for entity in path[:-1]:
            for yielded in check_yield_single(ns, entity):
                yield yielded

        entity = path[-1]

        if action.action_type == "empty":
            yield "{0}".format(entity.plural)
            return

        if action.action_type == "collection":
            yield "{0}/{1}".format(entity.plural, action.name)
            return

        if action.action_type == "single":
            for yielded in check_yield_single(ns, entity):
                yield yielded
            return

    def build_uri(self, ns, path, action):
        return "/" + "/".join(self._yield_uri_parts(ns, path, action))

    def format_body(self, body_dict):
        new_dict = dict()

        for key, value in body_dict.items():
            key_path = key.split(".")

            step_dict = new_dict

            for step in key_path[:-1]:
                try:
                    step_dict = step_dict[step]
                except KeyError:
                    step_dict[step] = dict()
                    step_dict = step_dict[step]

            step_dict[key_path[-1]] = value

        return new_dict

    def run(self, ns):
        which = ns.which

        delattr(ns, "which")

        uri_name, path, action = which

        uri = self.build_uri(ns, path, action)

        method, with_body = self.method_map.get(action.method)

        body = None

        if with_body:
            body = self.format_body(dict(ns.__dict__))

        self.impl.request(uri_name, method, uri, body)
