/**
 * Terraform variables for Bedrock Agent deployment
 */

##############################################################################
# General Configuration
##############################################################################

variable "aws_region" {
  description = "AWS region where the Bedrock Agent will be deployed"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.aws_region))
    error_message = "AWS region must be a valid region identifier (e.g., us-east-1, eu-west-1)"
  }
}

variable "project_name" {
  description = "Name of the project (used for tagging)"
  type        = string
  default     = "bedrock-agentcore-ts"
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "test", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, test, staging, prod"
  }
}

##############################################################################
# Bedrock Agent Configuration
##############################################################################

variable "agent_name" {
  description = "Name of the Bedrock Agent"
  type        = string
  default     = "typescript-bedrock-agent"

  validation {
    condition     = can(regex("^[a-zA-Z0-9-_]+$", var.agent_name))
    error_message = "Agent name must contain only alphanumeric characters, hyphens, and underscores"
  }
}

variable "agent_description" {
  description = "Description of the Bedrock Agent"
  type        = string
  default     = "TypeScript-based AI agent powered by AWS Bedrock"
}

variable "agent_instruction" {
  description = "Instructions that guide the agent's behavior and responses"
  type        = string
  default     = <<-EOT
    You are a helpful AI assistant that provides information and answers questions.
    You should be concise, accurate, and helpful in your responses.
    If you don't know something, say so rather than making up information.
    Always maintain a professional and friendly tone.
  EOT
}

variable "agent_alias_name" {
  description = "Name of the agent alias (e.g., 'prod', 'dev', 'latest')"
  type        = string
  default     = "latest"

  validation {
    condition     = can(regex("^[a-zA-Z0-9-_]+$", var.agent_alias_name))
    error_message = "Agent alias name must contain only alphanumeric characters, hyphens, and underscores"
  }
}

##############################################################################
# Foundation Model Configuration
##############################################################################

variable "foundation_model_id" {
  description = "The foundation model ID to use for the agent"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"

  validation {
    condition = can(regex("^(anthropic\\.claude|amazon\\.titan|ai21\\.j2|cohere\\.command|meta\\.llama)", var.foundation_model_id))
    error_message = "Foundation model ID must be a valid Bedrock model identifier"
  }
}

##############################################################################
# Inference Configuration
##############################################################################

variable "enable_prompt_override" {
  description = "Enable prompt override configuration for fine-tuned control"
  type        = bool
  default     = false
}

variable "inference_temperature" {
  description = "Temperature for inference (0.0 to 1.0). Higher values make output more random"
  type        = number
  default     = 0.7

  validation {
    condition     = var.inference_temperature >= 0 && var.inference_temperature <= 1
    error_message = "Temperature must be between 0.0 and 1.0"
  }
}

variable "inference_top_p" {
  description = "Top P for nucleus sampling (0.0 to 1.0)"
  type        = number
  default     = 0.9

  validation {
    condition     = var.inference_top_p >= 0 && var.inference_top_p <= 1
    error_message = "Top P must be between 0.0 and 1.0"
  }
}

variable "inference_top_k" {
  description = "Top K for sampling. Limits to top K tokens"
  type        = number
  default     = 250

  validation {
    condition     = var.inference_top_k >= 0 && var.inference_top_k <= 500
    error_message = "Top K must be between 0 and 500"
  }
}

variable "inference_max_length" {
  description = "Maximum length of generated responses"
  type        = number
  default     = 2048

  validation {
    condition     = var.inference_max_length >= 1 && var.inference_max_length <= 4096
    error_message = "Max length must be between 1 and 4096"
  }
}

variable "inference_stop_sequences" {
  description = "List of stop sequences for response generation"
  type        = list(string)
  default     = []
}

##############################################################################
# Session Configuration
##############################################################################

variable "idle_session_ttl" {
  description = "Idle session timeout in seconds (60 to 3600)"
  type        = number
  default     = 600

  validation {
    condition     = var.idle_session_ttl >= 60 && var.idle_session_ttl <= 3600
    error_message = "Idle session TTL must be between 60 and 3600 seconds"
  }
}

##############################################################################
# CloudWatch Configuration
##############################################################################

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 7

  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180,
      365, 400, 545, 731, 1096, 1827, 2192, 2557,
      2922, 3288, 3653
    ], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch Logs retention period"
  }
}

##############################################################################
# Optional: KMS Encryption
##############################################################################

variable "kms_key_arn" {
  description = "ARN of KMS key for encrypting agent data (optional)"
  type        = string
  default     = null
}

##############################################################################
# Tags
##############################################################################

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
