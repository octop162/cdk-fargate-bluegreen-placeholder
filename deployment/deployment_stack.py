from typing_extensions import runtime

from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_codedeploy as codedeploy,
    aws_ecs as ecs,
    aws_iam as iam,
)
from constructs import Construct
from settings.constant import Constant


class DeploymentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ############################
        # CodeCommit
        ############################
        repository = codecommit.Repository(
            self,
            "ApplicationRepository",
            repository_name="ApplicationRepository")

        source_output = codepipeline.Artifact("SourceArtifact")
        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="ApplicationRepository",
            repository=repository,
            branch='develop',
            output=source_output
        )

        ############################
        # CodeBuild
        ############################
        # Role
        codeBuildRole = iam.Role(
            self, 'CodeBuildRole', assumed_by=iam.ServicePrincipal('codebuild.amazonaws.com'))
        codeBuildRole.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryFullAccess'))
        # AppBuild
        app_build_project = codebuild.PipelineProject(
            self, "AppBuildProject",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
            ),
            role=codeBuildRole,
            build_spec=codebuild.BuildSpec.from_source_filename(
                'buildspec.app.yml'),
            cache=codebuild.Cache.local(
                codebuild.LocalCacheMode.DOCKER_LAYER,
                codebuild.LocalCacheMode.CUSTOM,
            )
        )
        app_build_outputs = codepipeline.Artifact('AppBuildArtifact')
        app_build_action = codepipeline_actions.CodeBuildAction(
            action_name="AppBuildAction",
            project=app_build_project,
            input=source_output,
            outputs=[app_build_outputs],
        )
        # WebBuild
        web_build_project = codebuild.PipelineProject(
            self, "WebBuildProjec",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
            ),
            role=codeBuildRole,
            build_spec=codebuild.BuildSpec.from_source_filename(
                'buildspec.web.yml'),
            cache=codebuild.Cache.local(
                codebuild.LocalCacheMode.DOCKER_LAYER,
                codebuild.LocalCacheMode.CUSTOM,
            )
        )
        web_build_outputs = codepipeline.Artifact('WebBuildArtifact')
        web_build_action = codepipeline_actions.CodeBuildAction(
            action_name="WebBuildAction",
            project=web_build_project,
            input=source_output,
            outputs=[web_build_outputs],
        )

        ############################
        # CodePipeline
        ############################
        pipeline = codepipeline.Pipeline(
            self, "ApplicationPipeline",
            pipeline_name="ApplicationPipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name='Source',
                    actions=[
                        source_action
                    ],
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        app_build_action,
                        web_build_action,
                    ],
                ),
            ],
        )
        pipeline.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "appconfig:GetDeployment",
                    "appconfig:StartDeployment",
                    "appconfig:StopDeployment",
                    "autoscaling:*",
                    "cloudformation:*",
                    "cloudformation:CreateChangeSet",
                    "cloudformation:CreateStack",
                    "cloudformation:DeleteChangeSet",
                    "cloudformation:DeleteStack",
                    "cloudformation:DescribeChangeSet",
                    "cloudformation:DescribeStacks",
                    "cloudformation:ExecuteChangeSet",
                    "cloudformation:SetStackPolicy",
                    "cloudformation:UpdateStack",
                    "cloudformation:ValidateTemplate",
                    "cloudwatch:*",
                    "codebuild:BatchGetBuildBatches",
                    "codebuild:BatchGetBuilds",
                    "codebuild:StartBuild",
                    "codebuild:StartBuildBatch",
                    "codecommit:CancelUploadArchive",
                    "codecommit:GetBranch",
                    "codecommit:GetCommit",
                    "codecommit:GetRepository",
                    "codecommit:GetUploadArchiveStatus",
                    "codecommit:UploadArchive",
                    "codedeploy:CreateDeployment",
                    "codedeploy:GetApplication",
                    "codedeploy:GetApplicationRevision",
                    "codedeploy:GetDeployment",
                    "codedeploy:GetDeploymentConfig",
                    "codedeploy:RegisterApplicationRevision",
                    "codestar-connections:UseConnection",
                    "devicefarm:CreateUpload",
                    "devicefarm:GetRun",
                    "devicefarm:GetUpload",
                    "devicefarm:ListDevicePools",
                    "devicefarm:ListProjects",
                    "devicefarm:ScheduleRun",
                    "ec2:*",
                    "ecr:DescribeImages",
                    "ecs:*",
                    "elasticbeanstalk:*",
                    "elasticloadbalancing:*",
                    "lambda:InvokeFunction",
                    "lambda:ListFunctions",
                    "opsworks:CreateDeployment",
                    "opsworks:DescribeApps",
                    "opsworks:DescribeCommands",
                    "opsworks:DescribeDeployments",
                    "opsworks:DescribeInstances",
                    "opsworks:DescribeStacks",
                    "opsworks:UpdateApp",
                    "opsworks:UpdateStack",
                    "rds:*",
                    "s3:*",
                    "servicecatalog:CreateProvisioningArtifact",
                    "servicecatalog:DeleteProvisioningArtifact",
                    "servicecatalog:DescribeProvisioningArtifact",
                    "servicecatalog:ListProvisioningArtifacts",
                    "servicecatalog:UpdateProduct",
                    "sns:*",
                    "sqs:*",
                    "states:DescribeExecution",
                    "states:DescribeStateMachine",
                    "states:StartExecution",
                ],
                resources=["*"],
                effect=iam.Effect.ALLOW,
            )
        )
        pipeline.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "iam:PassRole",
                ],
                resources=["*"],
                effect=iam.Effect.ALLOW,
                # conditions={
                #     "StringEqualsIfExists": {
                #         "iam:PassedToService": [
                #             "cloudformation.amazonaws.com",
                #             "elasticbeanstalk.amazonaws.com",
                #             "ec2.amazonaws.com",
                #             "ecs-tasks.amazonaws.com"
                #         ]
                #     }
                # }
            )
        )
