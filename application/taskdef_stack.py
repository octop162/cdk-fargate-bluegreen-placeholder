from aws_cdk import (
    Stack,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
)
from constructs import Construct
from settings.constant import Constant


class ApplicationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Vpc
        vpc = ec2.Vpc.from_lookup(self, 'Vpc',
                                  vpc_id=Constant.VPC_ID,
                                  region=Constant.REGION
                                  )

        task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef", memory_limit_mib=1024, cpu=512)

        container_web = task_definition.add_container("web",
                                                      image=ecs.ContainerImage.from_ecr_repository(
                                                          ecr.Repository.from_repository_name(self, 'WebRepository', 'web-repository'))
                                                      )
        container_app = task_definition.add_container("app",
                                                      image=ecs.ContainerImage.from_ecr_repository(
                                                          ecr.Repository.from_repository_name(self, 'AppRepository', 'app-repository'))
                                                      )
        container_web.add_port_mappings(
            ecs.PortMapping(
                container_port=80,
                protocol=ecs.Protocol.TCP,
            )
        )
        container_app.add_port_mappings(
            ecs.PortMapping(
                container_port=3031,
                protocol=ecs.Protocol.TCP,
            )
        )
