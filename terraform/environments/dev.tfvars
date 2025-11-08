# Development Environment Configuration

aws_region   = "us-east-1"
project_name = "bedrock-agentcore-ts"
environment  = "dev"

agent_name        = "typescript-bedrock-agent-dev"
agent_alias_name  = "dev"
agent_description = "Development environment for TypeScript Bedrock Agent"

agent_instruction = <<-EOT
  You are a helpful AI assistant in a development environment.
  Provide detailed, technical responses and feel free to include examples.
  You can be more verbose to help with learning and debugging.
EOT

# Use cost-effective model for development
foundation_model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# Development settings
idle_session_ttl   = 600     # 10 minutes
log_retention_days = 7       # 1 week

# More creative responses for development/testing
inference_temperature = 0.8

additional_tags = {
  Environment = "Development"
  Purpose     = "Testing"
}
