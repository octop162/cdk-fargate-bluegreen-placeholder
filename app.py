#!/usr/bin/env python3

from aws_cdk import (
    App,
    Environment,
)

from settings.constant import Constant
from application.role_stack import RoleStack
from application.network_stack import NetworkStack
from application.application_stack import ApplicationStack
from application.ecr_stack import EcrStack
from deployment.deployment_stack import DeploymentStack

app = App()


# IAMロール
RoleStack(
    app,
    "RoleStack",
    env=Environment(account=Constant.ACCOUNT, region=Constant.REGION),
)

# ネットワーク構成
network_stack = NetworkStack(
    app,
    "NetworkStack",
    env=Environment(account=Constant.ACCOUNT, region=Constant.REGION),
)

# ECR
ecr_stack = EcrStack(
    app,
    "EcrStack",
    env=Environment(account=Constant.ACCOUNT, region=Constant.REGION),
)

# アプリケーション
application_stack = ApplicationStack(
    app,
    "ApplicationStack",
    env=Environment(account=Constant.ACCOUNT, region=Constant.REGION),
)
application_stack.add_dependency(network_stack)
application_stack.add_dependency(ecr_stack)

# デプロイメント
DeploymentStack(
    app,
    'DeploymentStack',
    env=Environment(account=Constant.ACCOUNT, region=Constant.REGION),
)

app.synth()
