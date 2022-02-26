from ipaddress import ip_address
from aws_cdk import (
    Stack,
    Duration,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
)
from constructs import Construct
from image.app.app import health
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

        cluster = ecs.Cluster(
            self, "EcsCluster",
            cluster_name="EcsCluster", vpc=vpc
        )

        task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef", memory_limit_mib=512, cpu=256)

        container_web = task_definition.add_container(
            "web",
            image=ecs.ContainerImage.from_ecr_repository(
                ecr.Repository.from_repository_name(self, 'WebRepository', 'web-repository'))
        )
        container_app = task_definition.add_container(
            "app",
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

        service = ecs.FargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=task_definition,
            deployment_controller=ecs.DeploymentController(
                type=ecs.DeploymentControllerType.CODE_DEPLOY,
            ),
        )

        ############################
        # Load Balancer
        ############################
        alb = elbv2.ApplicationLoadBalancer(
            self, "Alb",
            vpc=vpc,
            internet_facing=True,
        )

        health_check = elbv2.HealthCheck(
            enabled=True,
            interval=Duration.seconds(30),
            path='/',
            protocol=elbv2.Protocol.HTTP,
            healthy_http_codes='200',
            healthy_threshold_count=2,
            unhealthy_threshold_count=3,
            timeout=Duration.seconds(10),
        )

        main_listener = alb.add_listener(
            "MainListener",
            port=80,
            protocol=elbv2.Protocol.HTTP,
            open=True,
        )

        target_group1 = main_listener.add_targets(
            "Target1",
            port=80,
            targets=[service],
            health_check=health_check,
        )

        test_listener = alb.add_listener(
            "TestListener",
            port=20080,
            protocol=elbv2.Protocol.HTTP,
            open=True,
            default_action=elbv2.ListenerAction.forward(
                target_groups=[target_group1],
            )
        )

        target_group2 = elbv2.ApplicationTargetGroup(
            self, 'Target2',
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            vpc=vpc,
            health_check=health_check,
        )

        # ターゲットグループをロードバランサに関連付ける
        service.node.add_dependency(target_group1)
        service.node.add_dependency(target_group2)
        service.node.add_dependency(main_listener)
        service.node.add_dependency(test_listener)
