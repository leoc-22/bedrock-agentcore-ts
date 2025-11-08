# Production Environment Configuration

aws_region   = "us-east-1"
project_name = "bedrock-agentcore-ts"
environment  = "prod"

agent_name        = "typescript-bedrock-agent-prod"
agent_alias_name  = "prod"
agent_description = "Production TypeScript Bedrock Agent"

agent_instruction = <<-EOT
  You are a professional AI assistant providing accurate and helpful information.
  Be concise, accurate, and maintain a professional tone.
  Prioritize accuracy over creativity in your responses.
EOT

# Use balanced model for production
foundation_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

# Production settings
idle_session_ttl   = 1800    # 30 minutes
log_retention_days = 30      # 30 days

# More deterministic responses for production
inference_temperature = 0.5

additional_tags = {
  Environment    = "Production"
  Criticality    = "High"
  BackupRequired = "true"
}
