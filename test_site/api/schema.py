"""GrapQl schema.  """

import graphene

import graphene_django_tools


class Mutation(graphene.ObjectType):
    """Mutation """

    create_user = graphene_django_tools.auth.UserCreation.Field()
    update_user = graphene_django_tools.auth.UserUpdate.Field()


SCHEMA = graphene.Schema(
    query=graphene_django_tools.utils.EmptyQuery,
    mutation=Mutation,
    auto_camelcase=False)
