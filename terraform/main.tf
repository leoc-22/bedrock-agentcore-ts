/**
 * Main Terraform configuration for AWS Bedrock Agent
 *
 * This deploys a complete Bedrock Agent infrastructure including:
 * - Bedrock Agent with foundation model
 * - Agent Alias for deployment
 * - IAM roles and policies
 * - CloudWatch log groups
 */

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment to use S3 backend for state management
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "bedrock-agent/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

##############################################################################
# Data Sources
##############################################################################

# Get current AWS account ID and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Get the foundation model information
data "aws_bedrock_foundation_model" "agent_model" {
  model_id = var.foundation_model_id
}

##############################################################################
# IAM Role for Bedrock Agent
##############################################################################

resource "aws_iam_role" "bedrock_agent" {
  name               = "${var.agent_name}-role-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.bedrock_agent_trust.json
  description        = "IAM role for Bedrock Agent ${var.agent_name}"

  tags = {
    Name = "${var.agent_name}-role"
  }
}

# Trust policy allowing Bedrock to assume the role
data "aws_iam_policy_document" "bedrock_agent_trust" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:agent/*"]
    }
  }
}

# Policy for Bedrock Agent permissions
resource "aws_iam_role_policy" "bedrock_agent_policy" {
  name   = "${var.agent_name}-policy-${var.environment}"
  role   = aws_iam_role.bedrock_agent.id
  policy = data.aws_iam_policy_document.bedrock_agent_permissions.json
}

data "aws_iam_policy_document" "bedrock_agent_permissions" {
  # Allow invoking foundation model
  statement {
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream"
    ]
    resources = [
      data.aws_bedrock_foundation_model.agent_model.model_arn
    ]
  }

  # Allow CloudWatch Logs
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/bedrock/agents/${var.agent_name}*"
    ]
  }
}

##############################################################################
# CloudWatch Log Group
##############################################################################

resource "aws_cloudwatch_log_group" "bedrock_agent" {
  name              = "/aws/bedrock/agents/${var.agent_name}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.agent_name}-logs"
  }
}

##############################################################################
# Bedrock Agent
##############################################################################

resource "aws_bedrockagent_agent" "main" {
  agent_name              = var.agent_name
  agent_resource_role_arn = aws_iam_role.bedrock_agent.arn
  description             = var.agent_description
  foundation_model        = var.foundation_model_id
  instruction             = var.agent_instruction

  # Automatically prepare the agent after creation/updates
  prepare_agent = true

  # Idle session timeout (in seconds)
  idle_session_ttl_in_seconds = var.idle_session_ttl

  # Optional: Customer encryption key
  # customer_encryption_key_arn = var.kms_key_arn

  # Optional: Prompt override configuration
  dynamic "prompt_override_configuration" {
    for_each = var.enable_prompt_override ? [1] : []

    content {
      prompt_configurations {
        prompt_type     = "PRE_PROCESSING"
        prompt_state    = "ENABLED"
        prompt_creation_mode = "DEFAULT"

        inference_configuration {
          temperature     = var.inference_temperature
          top_p          = var.inference_top_p
          top_k          = var.inference_top_k
          max_length     = var.inference_max_length
          stop_sequences = var.inference_stop_sequences
        }
      }

      prompt_configurations {
        prompt_type     = "ORCHESTRATION"
        prompt_state    = "ENABLED"
        prompt_creation_mode = "DEFAULT"

        inference_configuration {
          temperature     = var.inference_temperature
          top_p          = var.inference_top_p
          top_k          = var.inference_top_k
          max_length     = var.inference_max_length
          stop_sequences = var.inference_stop_sequences
        }
      }
    }
  }

  tags = {
    Name        = var.agent_name
    Environment = var.environment
  }

  # Ensure IAM role and CloudWatch log group are created first
  depends_on = [
    aws_iam_role_policy.bedrock_agent_policy,
    aws_cloudwatch_log_group.bedrock_agent
  ]
}

##############################################################################
# Bedrock Agent Alias
##############################################################################

resource "aws_bedrockagent_agent_alias" "main" {
  agent_id         = aws_bedrockagent_agent.main.agent_id
  agent_alias_name = var.agent_alias_name
  description      = "Agent alias for ${var.environment} environment"

  # Optional: Route to specific agent version
  # routing_configuration {
  #   agent_version = "1"
  # }

  tags = {
    Name        = "${var.agent_name}-${var.agent_alias_name}"
    Environment = var.environment
  }

  # Wait for agent to be prepared before creating alias
  depends_on = [aws_bedrockagent_agent.main]
}

##############################################################################
# Outputs
##############################################################################

output "agent_id" {
  description = "The ID of the Bedrock Agent"
  value       = aws_bedrockagent_agent.main.agent_id
}

output "agent_arn" {
  description = "The ARN of the Bedrock Agent"
  value       = aws_bedrockagent_agent.main.agent_arn
}

output "agent_alias_id" {
  description = "The ID of the Bedrock Agent Alias"
  value       = aws_bedrockagent_agent_alias.main.agent_alias_id
}

output "agent_alias_arn" {
  description = "The ARN of the Bedrock Agent Alias"
  value       = aws_bedrockagent_agent_alias.main.agent_alias_arn
}

output "agent_role_arn" {
  description = "The ARN of the IAM role for the Bedrock Agent"
  value       = aws_iam_role.bedrock_agent.arn
}

output "log_group_name" {
  description = "The name of the CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.bedrock_agent.name
}
