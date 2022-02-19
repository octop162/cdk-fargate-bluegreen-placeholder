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

        ############################
        # ECS
        ############################
        cluster = ecs.Cluster(self, "EcsCluster", vpc=vpc)

        task_definition = ecs.FargateTaskDefinition(self, "TaskDef")

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

        service = ecs.FargateService(self, "FargateService",
                                     cluster=cluster,
                                     task_definition=task_definition,
                                     deployment_controller=ecs.DeploymentController(
                                         type=ecs.DeploymentControllerType.CODE_DEPLOY)
                                     )

        ############################
        # Load Balancer
        ############################
        alb = elbv2.ApplicationLoadBalancer(self, "Alb",
                                            vpc=vpc,
                                            internet_facing=True,
                                            )

        main_listener = alb.add_listener("MainListener",
                                         port=80,
                                         protocol=elbv2.Protocol.HTTP,
                                         open=True,
                                         )

        test_listener = alb.add_listener("TestListener",
                                         port=20080,
                                         protocol=elbv2.Protocol.HTTP,
                                         open=True,
                                         )

        target1 = main_listener.add_targets("ApplicationFleets1",
                                            port=80,
                                            targets=[service]
                                            )

        target2 = test_listener.add_targets("ApplicationFleets2",
                                            port=80,
                                            targets=[service]
                                            )
