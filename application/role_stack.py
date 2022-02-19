from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct
from settings.constant import Constant


class RoleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # SSM Role
        ssmRole = iam.Role(self, 'SsmRole', assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))
        ssmRole.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'))
