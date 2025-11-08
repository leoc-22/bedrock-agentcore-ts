# Terraform Infrastructure for AWS Bedrock Agent

This directory contains Terraform configurations to deploy your AWS Bedrock AgentCore Runtime infrastructure. **No more click-ops!** Everything is defined as code.

## Table of Contents

1. [What Gets Deployed](#what-gets-deployed)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [Managing Multiple Environments](#managing-multiple-environments)
7. [Outputs and Integration](#outputs-and-integration)
8. [Terraform State Management](#terraform-state-management)
9. [Cleanup](#cleanup)
10. [Advanced Configuration](#advanced-configuration)
11. [Troubleshooting](#troubleshooting)

---

## What Gets Deployed

This Terraform configuration deploys a complete Bedrock Agent infrastructure:

- ✅ **Bedrock Agent** with your chosen foundation model
- ✅ **Agent Alias** for environment-specific deployments
- ✅ **IAM Role and Policies** with least-privilege permissions
- ✅ **CloudWatch Log Group** for agent logging
- ✅ **Automatic Agent Preparation** ready to use immediately

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Your TypeScript App                    │
│              (bedrock-agentcore-ts)                     │
└────────────────────┬────────────────────────────────────┘
                     │ Invokes
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Bedrock Agent Alias                        │
│              (e.g., "dev", "prod")                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Bedrock Agent                              │
│   ┌──────────────────────────────────────────────┐     │
│   │  Foundation Model (Claude 3, etc.)           │     │
│   └──────────────────────────────────────────────┘     │
│   ┌──────────────────────────────────────────────┐     │
│   │  Agent Instructions                          │     │
│   └──────────────────────────────────────────────┘     │
└────────────────────┬────────────────────────────────────┘
                     │ Assumes Role
                     ▼
┌─────────────────────────────────────────────────────────┐
│              IAM Role                                   │
│   • InvokeModel permissions                            │
│   • CloudWatch Logs permissions                        │
└────────────────────┬────────────────────────────────────┘
                     │ Logs to
                     ▼
┌─────────────────────────────────────────────────────────┐
│          CloudWatch Log Group                           │
│          /aws/bedrock/agents/...                        │
└─────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### 1. Terraform Installation

Install Terraform 1.0 or later:

```bash
# macOS (Homebrew)
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.9.0/terraform_1.9.0_linux_amd64.zip
unzip terraform_1.9.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Windows (Chocolatey)
choco install terraform

# Verify installation
terraform version
```

### 2. AWS CLI Configuration

```bash
# Configure AWS credentials
aws configure

# Verify access
aws sts get-caller-identity
```

### 3. AWS Permissions

Your AWS user/role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:CreateAgent",
        "bedrock:UpdateAgent",
        "bedrock:DeleteAgent",
        "bedrock:GetAgent",
        "bedrock:PrepareAgent",
        "bedrock:CreateAgentAlias",
        "bedrock:UpdateAgentAlias",
        "bedrock:DeleteAgentAlias",
        "bedrock:GetAgentAlias",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PutRolePolicy",
        "iam:GetRole",
        "iam:DeleteRole",
        "iam:DeleteRolePolicy",
        "iam:PassRole",
        "logs:CreateLogGroup",
        "logs:DeleteLogGroup",
        "logs:PutRetentionPolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

### 4. Bedrock Model Access

Enable access to foundation models in AWS Bedrock Console:
1. Go to AWS Bedrock Console → Model access
2. Request access to your desired models (e.g., Claude 3)
3. Wait for approval (usually instant for most models)

---

## Quick Start

### 1. Navigate to Terraform Directory

```bash
cd terraform
```

### 2. Create Your Configuration

```bash
# Copy the example tfvars file
cp terraform.tfvars.example terraform.tfvars

# Edit with your preferred editor
nano terraform.tfvars
```

### 3. Initialize Terraform

```bash
terraform init
```

This downloads the AWS provider and prepares your workspace.

### 4. Review the Plan

```bash
terraform plan
```

Review what Terraform will create. You should see:
- 1 Bedrock Agent
- 1 Agent Alias
- 1 IAM Role
- 1 IAM Role Policy
- 1 CloudWatch Log Group

### 5. Deploy!

```bash
terraform apply
```

Type `yes` when prompted. Deployment takes ~2-3 minutes.

### 6. Get Your Agent IDs

```bash
terraform output
```

Copy the `agent_id` and `agent_alias_id` to your `.env` file:

```bash
# Automatically update .env file
terraform output -raw env_file_content >> ../.env
```

### 7. Test Your Agent

```bash
cd ..
npm test
```

🎉 **Done!** Your Bedrock Agent is deployed and ready to use.

---

## Configuration

### Basic Configuration (terraform.tfvars)

```hcl
# Required
aws_region  = "us-east-1"
environment = "dev"

# Agent configuration
agent_name = "my-awesome-agent"
agent_instruction = "You are a helpful assistant..."

# Choose your model
foundation_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
```

### Available Foundation Models

```hcl
# Claude 3.5 Sonnet (Latest, most capable)
foundation_model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Claude 3 Sonnet (Balanced)
foundation_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

# Claude 3 Haiku (Fast & Cost-effective)
foundation_model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# Claude 3 Opus (Most capable, higher cost)
foundation_model_id = "anthropic.claude-3-opus-20240229-v1:0"
```

### Customizing Agent Behavior

Edit the `agent_instruction` variable in `terraform.tfvars`:

```hcl
agent_instruction = <<-EOT
  You are a specialized AWS cloud architecture assistant.

  Your responsibilities:
  - Provide best practices for AWS architecture
  - Explain AWS services in simple terms
  - Suggest cost-optimization strategies
  - Help debug common AWS issues

  Guidelines:
  - Be concise but thorough
  - Provide code examples when relevant
  - Always consider security implications
  - Mention cost implications when significant
EOT
```

---

## Deployment

### Development Environment

```bash
# Use dev-specific configuration
terraform apply -var-file="environments/dev.tfvars"
```

### Production Environment

```bash
# Use prod-specific configuration
terraform apply -var-file="environments/prod.tfvars"
```

### Custom Variables

Override any variable on the command line:

```bash
terraform apply \
  -var="agent_name=custom-agent" \
  -var="foundation_model_id=anthropic.claude-3-haiku-20240307-v1:0" \
  -var="log_retention_days=30"
```

---

## Managing Multiple Environments

### Using Workspaces

```bash
# Create workspaces for different environments
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch between environments
terraform workspace select dev
terraform apply -var-file="environments/dev.tfvars"

terraform workspace select prod
terraform apply -var-file="environments/prod.tfvars"

# List workspaces
terraform workspace list
```

### Using Separate State Files

```bash
# Development
terraform apply -var-file="environments/dev.tfvars" \
  -state="terraform-dev.tfstate"

# Production
terraform apply -var-file="environments/prod.tfvars" \
  -state="terraform-prod.tfstate"
```

### Using Separate Directories

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf -> ../../main.tf (symlink)
│   │   ├── variables.tf -> ../../variables.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf -> ../../main.tf
│       ├── variables.tf -> ../../variables.tf
│       └── terraform.tfvars
```

---

## Outputs and Integration

### View All Outputs

```bash
terraform output
```

### Get Specific Output

```bash
# Get Agent ID
terraform output -raw agent_id

# Get Agent Alias ID
terraform output -raw agent_alias_id

# Get formatted .env content
terraform output -raw env_file_content
```

### Automatically Update .env File

```bash
# Append to .env file in parent directory
terraform output -raw env_file_content >> ../.env

# Or create new .env file
terraform output -raw env_file_content > ../.env
```

### Integration with CI/CD

```bash
# Export as environment variables
export BEDROCK_AGENT_ID=$(terraform output -raw agent_id)
export BEDROCK_AGENT_ALIAS_ID=$(terraform output -raw agent_alias_id)
export AWS_REGION=$(terraform output -raw aws_region)

# Use in scripts
echo "Testing agent ${BEDROCK_AGENT_ID}..."
npm test
```

### Quick Start Commands

```bash
terraform output quick_start_commands
```

This displays helpful next steps and testing commands.

---

## Terraform State Management

### Local State (Default)

By default, Terraform stores state in `terraform.tfstate` locally.

**Pros:** Simple, no setup
**Cons:** Not suitable for teams, no locking

### Remote State with S3 (Recommended)

#### 1. Create S3 Bucket and DynamoDB Table

```bash
# Create S3 bucket for state
aws s3 mb s3://my-terraform-state-bucket --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-terraform-state-bucket \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

#### 2. Configure Backend in main.tf

Uncomment and update the backend configuration in `main.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "bedrock-agent/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

#### 3. Initialize with Backend

```bash
terraform init -migrate-state
```

---

## Cleanup

### Destroy All Resources

```bash
# Review what will be destroyed
terraform plan -destroy

# Destroy resources
terraform destroy
```

Type `yes` when prompted.

### Destroy Specific Resources

```bash
# Destroy only the agent alias
terraform destroy -target=aws_bedrockagent_agent_alias.main

# Destroy only CloudWatch log group
terraform destroy -target=aws_cloudwatch_log_group.bedrock_agent
```

### Verify Cleanup

```bash
# Check if agent still exists
aws bedrock-agent list-agents --region us-east-1

# Check if IAM role was deleted
aws iam get-role --role-name typescript-bedrock-agent-role-dev
```

---

## Advanced Configuration

### Enable Prompt Override for Fine-Tuned Control

```hcl
enable_prompt_override = true
inference_temperature  = 0.8
inference_top_p        = 0.9
inference_top_k        = 250
inference_max_length   = 2048
```

### Custom KMS Encryption

```hcl
kms_key_arn = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
```

### Extended Log Retention

```hcl
log_retention_days = 90  # 90 days
```

### Custom Tags

```hcl
additional_tags = {
  Team        = "AI-Engineering"
  CostCenter  = "R&D"
  Compliance  = "SOC2"
  DataClass   = "Internal"
}
```

---

## Troubleshooting

### Issue: "Error: Invalid provider configuration"

**Cause:** AWS credentials not configured

**Solution:**
```bash
aws configure
aws sts get-caller-identity
```

### Issue: "Error: creating Bedrock Agent: AccessDeniedException"

**Cause:** Insufficient IAM permissions

**Solution:** Ensure your user has the permissions listed in Prerequisites

### Issue: "Error: Invalid foundation_model_id"

**Cause:** Model not available in your region or account

**Solution:**
1. Check model availability: `aws bedrock list-foundation-models --region us-east-1`
2. Request access in Bedrock Console
3. Use a different model

### Issue: "Agent creation succeeds but alias fails"

**Cause:** Agent not fully prepared before alias creation

**Solution:** The Terraform config includes `depends_on` and `prepare_agent = true`. If still failing:

```bash
# Wait a bit and retry
sleep 30
terraform apply
```

### Issue: "Error: state lock"

**Cause:** Previous Terraform run didn't complete

**Solution:**
```bash
# Force unlock (use with caution!)
terraform force-unlock <LOCK_ID>
```

### Issue: Cannot destroy resources

**Cause:** Resources have dependencies

**Solution:**
```bash
# Destroy in reverse order
terraform destroy -target=aws_bedrockagent_agent_alias.main
terraform destroy -target=aws_bedrockagent_agent.main
terraform destroy
```

### Debugging

```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform apply

# Save logs to file
export TF_LOG_PATH=./terraform-debug.log
terraform apply
```

---

## Best Practices

1. **Use Remote State:** Always use S3 backend for team environments
2. **Version Control:** Commit `*.tf` files, NOT `*.tfvars` or `*.tfstate`
3. **Environment Separation:** Use workspaces or separate directories
4. **Plan First:** Always run `terraform plan` before `apply`
5. **Tag Everything:** Use consistent tagging for cost tracking
6. **Lock Versions:** Pin provider versions in `main.tf`
7. **Review Changes:** Check `terraform plan` output carefully
8. **Test in Dev First:** Always test changes in dev before prod

---

## Additional Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Bedrock Agent Docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)
- [AWS Bedrock Model Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)

---

## Support

For issues with:
- **Terraform:** Check Terraform documentation or open an issue
- **AWS Bedrock:** Check AWS Bedrock documentation or AWS Support
- **This Project:** See main [README.md](../README.md) or open an issue on GitHub
