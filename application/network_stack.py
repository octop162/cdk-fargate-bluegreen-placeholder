from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct
from settings.constant import Constant


class NetworkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ############################
        # Public
        ############################
        public_subnet_1 = ec2.PublicSubnet(self, "PublicSubnet1",
                                           availability_zone=Constant.AZ1,
                                           cidr_block='10.0.0.0/24',
                                           vpc_id=Constant.VPC_ID,
                                           )
        public_subnet_2 = ec2.PublicSubnet(self, "PublicSubnet2",
                                           availability_zone=Constant.AZ2,
                                           cidr_block='10.0.1.0/24',
                                           vpc_id=Constant.VPC_ID,
                                           )

        # IGW
        igw = ec2.CfnInternetGateway(self, "InternetGateway")
        att = ec2.CfnVPCGatewayAttachment(self, 'VPCGatewayAttachment',
                                          internet_gateway_id=igw.ref,
                                          vpc_id=Constant.VPC_ID)
        public_subnet_1.add_default_internet_route(igw.ref, att)
        public_subnet_2.add_default_internet_route(igw.ref, att)

        # NAT
        nat = public_subnet_1.add_nat_gateway()

        ############################
        # Private
        ############################
        private_subnet_1 = ec2.PrivateSubnet(self, "PrivateSubnet1",
                                             availability_zone=Constant.AZ1,
                                             cidr_block='10.0.2.0/24',
                                             vpc_id=Constant.VPC_ID,
                                             )
        private_subnet_2 = ec2.PrivateSubnet(self, "PrivateSubnet2",
                                             availability_zone=Constant.AZ2,
                                             cidr_block='10.0.3.0/24',
                                             vpc_id=Constant.VPC_ID,
                                             )

        # NAT ROUTE
        private_subnet_1.add_default_nat_route(nat.ref)
        private_subnet_2.add_default_nat_route(nat.ref)
