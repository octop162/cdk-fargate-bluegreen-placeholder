from ipaddress import ip_address
from aws_cdk import (
    Stack,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
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
        # Load Balancer
        ############################
        alb = elbv2.ApplicationLoadBalancer(
            self, "Alb",
            vpc=vpc,
            internet_facing=True,
        )

        target_group1 = elbv2.ApplicationTargetGroup(
            self, 'Target1',
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            vpc=vpc,
        )

        target_group2 = elbv2.ApplicationTargetGroup(
            self, 'Target2',
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            vpc=vpc,
        )

        main_listener = alb.add_listener(
            "MainListener",
            port=80,
            protocol=elbv2.Protocol.HTTP,
            open=True,
            default_action=elbv2.ListenerAction.forward(
                target_groups=[target_group1],
            )
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

        ############################
        # ECS
        ############################

        service_security_group = ec2.SecurityGroup(
            self, 'ServiceSecurtyGroup',
            vpc=vpc,
        )
        service_security_group.connections.allow_from(
            alb,
            ec2.Port.tcp(80),
        )

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

        service = ecs.CfnService(
            self, "Service",
            cluster=cluster.cluster_name,
            desired_count=1,
            deployment_controller=ecs.CfnService.DeploymentControllerProperty(
                type='CODE_DEPLOY'
            ),
            launch_type='FARGATE',
            propagate_tags='SERVICE',
            task_definition=task_definition.task_definition_arn,
            load_balancers=[
                ecs.CfnService.LoadBalancerProperty(
                    container_name=task_definition.default_container.container_name,
                    container_port=task_definition.default_container.container_port,
                    target_group_arn=target_group1.target_group_arn,
                )
            ],
            network_configuration=ecs.CfnService.NetworkConfigurationProperty(
                awsvpc_configuration=ecs.CfnService.AwsVpcConfigurationProperty(
                    subnets=vpc.select_subnets(
                        subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT).subnet_ids,
                    assign_public_ip="DISABLED",
                    security_groups=[
                        service_security_group.security_group_id,
                    ]
                )
            )
        )
        service.node.add_dependency(target_group1)
        service.node.add_dependency(target_group2)
        service.node.add_dependency(main_listener)
        service.node.add_dependency(test_listener)

        task_set1 = ecs.CfnTaskSet(
            self, 'TaskSet1',
            cluster=cluster.cluster_name,
            service=service.attr_name,
            scale=ecs.CfnTaskSet.ScaleProperty(
                unit="PERCENT", value=100,
            ),
            task_definition=task_definition.task_definition_arn,
            launch_type="FARGATE",
            load_balancers=[
                ecs.CfnTaskSet.LoadBalancerProperty(
                    container_name=task_definition.default_container.container_name,
                    container_port=task_definition.default_container.container_port,
                    target_group_arn=target_group1.target_group_arn,
                )
            ],
        )

        # task_set2 = ecs.CfnTaskSet(
        #     self, 'TaskSet2',
        #     cluster=cluster.cluster_name,
        #     service=service.attr_name,
        #     scale=ecs.CfnTaskSet.ScaleProperty(
        #         unit="PERCENT", value=100,
        #     ),
        #     task_definition=task_definition.task_definition_arn,
        #     launch_type="FARGATE",
        #     load_balancers=[
        #         ecs.CfnTaskSet.LoadBalancerProperty(
        #             container_name=task_definition.default_container.container_name,
        #             container_port=task_definition.default_container.container_port,
        #             target_group_arn=target_group1.target_group_arn,
        #         )
        #     ],
        # )

        # ecs.CfnPrimaryTaskSet(
        #     self, 'PrimaryTaskSet',
        #     cluster=cluster.cluster_name,
        #     service=service.attr_name,
        #     task_set_id=task_set1.attr_id,
        # )
