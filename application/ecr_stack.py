from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_ecr as ecr
)
from constructs import Construct
from settings.constant import Constant


class EcrStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecr.Repository(self, 'AppRepository',
                       repository_name='app-repository',
                       removal_policy=RemovalPolicy.DESTROY,
                       )

        ecr.Repository(self, 'WebRepository',
                       repository_name='web-repository',
                       removal_policy=RemovalPolicy.DESTROY,
                       )

        ecr.Repository(self, 'FirelensRepository',
                       repository_name='firelens-repository',
                       removal_policy=RemovalPolicy.DESTROY,
                       )
