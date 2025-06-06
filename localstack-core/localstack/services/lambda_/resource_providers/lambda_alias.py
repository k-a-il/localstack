# LocalStack Resource Provider Scaffolding v2
from __future__ import annotations

from pathlib import Path
from typing import Optional, TypedDict

import localstack.services.cloudformation.provider_utils as util
from localstack.services.cloudformation.resource_provider import (
    OperationStatus,
    ProgressEvent,
    ResourceProvider,
    ResourceRequest,
)


class LambdaAliasProperties(TypedDict):
    FunctionName: Optional[str]
    FunctionVersion: Optional[str]
    Name: Optional[str]
    Description: Optional[str]
    Id: Optional[str]
    ProvisionedConcurrencyConfig: Optional[ProvisionedConcurrencyConfiguration]
    RoutingConfig: Optional[AliasRoutingConfiguration]


class ProvisionedConcurrencyConfiguration(TypedDict):
    ProvisionedConcurrentExecutions: Optional[int]


class VersionWeight(TypedDict):
    FunctionVersion: Optional[str]
    FunctionWeight: Optional[float]


class AliasRoutingConfiguration(TypedDict):
    AdditionalVersionWeights: Optional[list[VersionWeight]]


REPEATED_INVOCATION = "repeated_invocation"


class LambdaAliasProvider(ResourceProvider[LambdaAliasProperties]):
    TYPE = "AWS::Lambda::Alias"  # Autogenerated. Don't change
    SCHEMA = util.get_schema_path(Path(__file__))  # Autogenerated. Don't change

    def create(
        self,
        request: ResourceRequest[LambdaAliasProperties],
    ) -> ProgressEvent[LambdaAliasProperties]:
        """
        Create a new resource.

        Primary identifier fields:
          - /properties/Id

        Required properties:
          - FunctionName
          - FunctionVersion
          - Name

        Create-only properties:
          - /properties/Name
          - /properties/FunctionName

        Read-only properties:
          - /properties/Id



        """
        model = request.desired_state
        lambda_ = request.aws_client_factory.lambda_

        create_params = util.select_attributes(
            model, ["FunctionName", "FunctionVersion", "Name", "Description", "RoutingConfig"]
        )

        ctx = request.custom_context
        if not ctx.get(REPEATED_INVOCATION):
            result = lambda_.create_alias(**create_params)
            model["Id"] = result["AliasArn"]
            ctx[REPEATED_INVOCATION] = True

            if model.get("ProvisionedConcurrencyConfig"):
                lambda_.put_provisioned_concurrency_config(
                    FunctionName=model["FunctionName"],
                    Qualifier=model["Name"],
                    ProvisionedConcurrentExecutions=model["ProvisionedConcurrencyConfig"][
                        "ProvisionedConcurrentExecutions"
                    ],
                )

            return ProgressEvent(
                status=OperationStatus.IN_PROGRESS,
                resource_model=model,
                custom_context=ctx,
            )

        if ctx.get(REPEATED_INVOCATION) and model.get("ProvisionedConcurrencyConfig"):
            # get provisioned config status
            result = lambda_.get_provisioned_concurrency_config(
                FunctionName=model["FunctionName"],
                Qualifier=model["Name"],
            )
            if result["Status"] == "IN_PROGRESS":
                return ProgressEvent(
                    status=OperationStatus.IN_PROGRESS,
                    resource_model=model,
                )
            elif result["Status"] == "READY":
                return ProgressEvent(
                    status=OperationStatus.SUCCESS,
                    resource_model=model,
                )
            else:
                return ProgressEvent(
                    status=OperationStatus.FAILED,
                    resource_model=model,
                    message="",
                    error_code="VersionStateFailure",  # TODO: not parity tested
                )

        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resource_model=model,
        )

    def read(
        self,
        request: ResourceRequest[LambdaAliasProperties],
    ) -> ProgressEvent[LambdaAliasProperties]:
        """
        Fetch resource information


        """
        raise NotImplementedError

    def delete(
        self,
        request: ResourceRequest[LambdaAliasProperties],
    ) -> ProgressEvent[LambdaAliasProperties]:
        """
        Delete a resource


        """
        model = request.desired_state
        lambda_ = request.aws_client_factory.lambda_

        try:
            # provisioned concurrency is automatically deleted upon deleting a function alias
            lambda_.delete_alias(
                FunctionName=model["FunctionName"],
                Name=model["Name"],
            )
        except lambda_.exceptions.ResourceNotFoundException:
            pass

        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resource_model=request.previous_state,
        )

    def update(
        self,
        request: ResourceRequest[LambdaAliasProperties],
    ) -> ProgressEvent[LambdaAliasProperties]:
        """
        Update a resource


        """
        raise NotImplementedError
