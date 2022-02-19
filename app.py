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

app = App()


# IAMロール
RoleStack(
    app,
    "RoleStack",
    env=Environment(account=Constant.ACCOUNT, region=Constant.REGION),
)

# ネットワーク構成
NetworkStack(
    app,
    "NetworkStack",
    env=Environment(account=Constant.ACCOUNT, region=Constant.REGION),
)

# ECR
EcrStack(
    app,
    "EcrStack",
    env=Environment(account=Constant.ACCOUNT, region=Constant.REGION),
)

# アプリケーション
ApplicationStack(
    app,
    "ApplicationStack",
    env=Environment(account=Constant.ACCOUNT, region=Constant.REGION),
)

app.synth()
