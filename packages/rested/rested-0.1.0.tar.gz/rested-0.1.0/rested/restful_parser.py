import argparse

from rested.action import Action

from rested.relation import OneToOne
from rested.relation import OneToMany
from rested.relation import ManyToMany

DEFAULT_ACTIONS = [
    Action("list",
           method="read",
           help="List all {entity.name} entities",
           action_type="empty"),
    Action("create",
           method="write",
           help="Create {entity.name}",
           inherit_fields=True,
           action_type="empty"),
    Action("show",
           method="read",
           help="Show {entity.name}"),
    Action("update",
           method="update",
           help="Update {entity.name}",
           inherit_fields=True,
           action_type="single"),
    Action("delete",
           method="delete",
           help="Delete a single {entity.name}"),
]

LIST_ACTIONS = [
    Action("add",
           help="Add a {rel_entity.name}"),
    Action("remove",
           help="Remove a {rel_entity.name}")
]


def create_restful_parser(entity, relations):
    parser = argparse.ArgumentParser()
    _create_restful_parser(entity, relations, parser)
    return parser


def _create_restful_parser(entity, relations, parser):
    queue = [(entity, relations, parser, entity.plural, [entity])]

    while queue:
        entity, relations, parser, ns, path = queue.pop()

        subparsers = parser.add_subparsers()

        p = {
            "entity": entity
        }

        actions = DEFAULT_ACTIONS + entity.actions
        one_to_one = list()

        for relation, (rel_entity, rel_relations) in relations:
            if type(relation) == OneToOne:
                one_to_one.append(rel_entity)
                continue

            if type(relation) == OneToMany:
                rel_parser = subparsers.add_parser(
                    relation.name,
                    help=relation.help.format(**p))

                rel_parser.add_argument(
                    entity.singular,
                    help=entity.help.format(**p))

                rel_ns = "{0}_{1}".format(ns, rel_entity.plural)
                rel_path = path + [rel_entity]

                queue.insert(0, (rel_entity, rel_relations, rel_parser,
                                 rel_ns, rel_path))
                continue

            if type(relation) == ManyToMany:
                rel_p = dict(p)
                rel_p["rel_entity"] = rel_entity

                rel_parser = subparsers.add_parser(relation.name)
                rel_parser.add_argument(
                    entity.singular,
                    help=entity.help.format(**rel_p))

                rel_subparsers = rel_parser.add_subparsers()

                for action in LIST_ACTIONS:
                    command = rel_subparsers.add_parser(
                        action.name,
                        help=action.help.format(**rel_p))

                    rel_ns = "{0}_{1}_{2}".format(
                        ns,
                        action.name,
                        rel_entity.plural)

                    command.set_defaults(which=(rel_ns, path, action))

                continue

            raise TypeError(relation)

        for action in actions:
            command = subparsers.add_parser(
                action.name,
                help=action.help.format(**p))

            action_ns = "{0}_{1}".format(ns, action.name)

            command.set_defaults(which=(action_ns, path, action))

            if action.action_type == "single":
                command.add_argument(
                    entity.singular,
                    help=entity.help)

            for argument in action.arguments:
                command.add_argument(argument.name, help=argument.help)

            fields = list()

            if action.inherit_fields:
                fields.extend((f.name, f.name, f) for f in entity.fields)

                for rel_entity in one_to_one:
                    for field in rel_entity.fields:
                        name = "{0}-{1}".format(
                            rel_entity.singular,
                            field.name)

                        dest_name = "{0}.{1}".format(
                            rel_entity.singular,
                            field.name)

                        fields.append((name, dest_name, field))

            fields += list(action.fields)

            for name, dest_name, field in fields:
                command.add_argument(
                    "--{0}".format(name),
                    dest=dest_name,
                    metavar=field.field_type.metavar,
                    type=field.field_type,
                    help=field.help.format(**p),
                    required=field.required,
                    default=field.default)

    return parser
