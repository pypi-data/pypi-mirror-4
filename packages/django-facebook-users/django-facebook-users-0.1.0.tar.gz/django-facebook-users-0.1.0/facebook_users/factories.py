from models import User
import factory
import random

class UserFactory(factory.Factory):
    FACTORY_FOR = User

    graph_id = factory.Sequence(lambda n: n)
    gender = random.choice(['male','female'])