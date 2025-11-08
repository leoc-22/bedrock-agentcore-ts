# AWS Bedrock AgentCore TypeScript - Deployment Guide

This comprehensive guide walks you through setting up, configuring, and deploying a TypeScript-based AI agent using AWS Bedrock AgentCore Runtime.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Setup](#aws-setup)
3. [Local Development Setup](#local-development-setup)
4. [Configuration](#configuration)
5. [Running Examples](#running-examples)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Prerequisites

### Required Software

- **Node.js**: Version 18.x or higher
- **npm**: Version 9.x or higher (comes with Node.js)
- **AWS Account**: Active AWS account with billing enabled
- **AWS CLI**: Version 2.x (optional but recommended)

### Required AWS Permissions

Your AWS IAM user/role needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeAgent",
        "bedrock:GetAgent",
        "bedrock:ListAgents"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## AWS Setup

### Step 1: Create a Bedrock Agent

1. **Navigate to AWS Bedrock Console**
   - Open the AWS Console
   - Go to Amazon Bedrock service
   - Select "Agents" from the left sidebar

2. **Create a New Agent**
   ```
   - Click "Create Agent"
   - Agent name: my-typescript-agent
   - Description: TypeScript-powered AI agent
   - IAM role: Create a new role or use existing
   - Model: Select Claude 3 Sonnet or your preferred model
   ```

3. **Configure Agent Instructions**
   - Add instructions for how your agent should behave
   - Example:
     ```
     You are a helpful AI assistant that provides information about AWS services.
     Answer questions concisely and accurately. If you don't know something, say so.
     ```

4. **Add Knowledge Bases (Optional)**
   - If you want your agent to access specific documents:
     - Create a knowledge base
     - Upload documents to S3
     - Connect the knowledge base to your agent

5. **Add Action Groups (Optional)**
   - Define custom tools/functions your agent can use
   - Connect to Lambda functions or API endpoints

6. **Create Agent Alias**
   ```
   - Click "Create Alias"
   - Alias name: prod (or dev, test, etc.)
   - Version: Select the agent version
   - Click "Create"
   ```

7. **Note Your IDs**
   - Copy the **Agent ID** (format: `XXXXXXXXXX`)
   - Copy the **Agent Alias ID** (format: `YYYYYYYYYY`)
   - You'll need these for configuration

### Step 2: Configure AWS Credentials

#### Option A: Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

#### Option B: AWS Credentials File

Create/edit `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key

[bedrock-agent]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
```

Create/edit `~/.aws/config`:

```ini
[default]
region = us-east-1

[profile bedrock-agent]
region = us-east-1
```

#### Option C: IAM Role (for EC2/ECS)

If running on AWS infrastructure, attach an IAM role with the required permissions.

---

## Local Development Setup

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd bedrock-agentcore-ts

# Install dependencies
npm install
```

### Step 2: Environment Configuration

Create a `.env` file in the root directory:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default  # Optional: Use specific AWS profile

# Bedrock Agent Configuration
BEDROCK_AGENT_ID=YOUR_AGENT_ID
BEDROCK_AGENT_ALIAS_ID=YOUR_AGENT_ALIAS_ID

# Optional: Use specific AWS credentials (not recommended for production)
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
```

Replace `YOUR_AGENT_ID` and `YOUR_AGENT_ALIAS_ID` with the values from AWS Console.

### Step 3: Build the Project

```bash
# Build TypeScript to JavaScript
npm run build
```

This compiles TypeScript files from `src/` to JavaScript in `dist/`.

---

## Configuration

### Basic Configuration

```typescript
import { BedrockAgentRuntime, AgentConfig } from './src';

const config: AgentConfig = {
  agentId: process.env.BEDROCK_AGENT_ID!,
  agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID!,
  region: 'us-east-1',
  enableTrace: false,  // Set to true for debugging
};

const agent = new BedrockAgentRuntime(config);
```

### Advanced Configuration

```typescript
const config: AgentConfig = {
  agentId: process.env.BEDROCK_AGENT_ID!,
  agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID!,
  region: process.env.AWS_REGION || 'us-east-1',
  sessionId: 'custom-session-id',  // Optional: Use specific session
  enableTrace: true,  // Enable trace for debugging
};
```

---

## Running Examples

### Example 1: Simple Agent

```bash
# Using ts-node (development)
npm run dev

# Or run compiled version
npm start

# Or run directly
node dist/examples/simple-agent.js
```

### Example 2: Streaming Agent

```bash
# Development
npx ts-node src/examples/streaming-agent.ts

# Production
node dist/examples/streaming-agent.js
```

### Example 3: Session State Agent

```bash
# Development
npx ts-node src/examples/session-state-agent.ts

# Production
node dist/examples/session-state-agent.js
```

### Creating Your Own Agent

```typescript
import { BedrockAgentRuntime } from './src';

async function myAgent() {
  const agent = new BedrockAgentRuntime({
    agentId: process.env.BEDROCK_AGENT_ID!,
    agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID!,
    region: 'us-east-1',
  });

  const response = await agent.invoke({
    inputText: 'Your question here',
  });

  console.log(response.completion);
}

myAgent();
```

---

## Production Deployment

### Option 1: AWS Lambda

1. **Create Lambda Function**

```bash
# Install dependencies for Lambda
npm install --production

# Create deployment package
npm run build
zip -r function.zip dist/ node_modules/ package.json
```

2. **Lambda Handler** (`lambda.ts`):

```typescript
import { BedrockAgentRuntime } from './src';

export const handler = async (event: any) => {
  const agent = new BedrockAgentRuntime({
    agentId: process.env.BEDROCK_AGENT_ID!,
    agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID!,
    region: process.env.AWS_REGION || 'us-east-1',
  });

  const response = await agent.invoke({
    inputText: event.query,
  });

  return {
    statusCode: 200,
    body: JSON.stringify({
      response: response.completion,
      sessionId: response.sessionId,
    }),
  };
};
```

3. **Deploy to Lambda**

```bash
aws lambda create-function \
  --function-name bedrock-agent-ts \
  --runtime nodejs18.x \
  --handler dist/lambda.handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-bedrock-role \
  --environment Variables="{BEDROCK_AGENT_ID=YOUR_AGENT_ID,BEDROCK_AGENT_ALIAS_ID=YOUR_ALIAS_ID}"
```

### Option 2: AWS ECS/Fargate

1. **Create Dockerfile**:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .
RUN npm run build

CMD ["node", "dist/examples/simple-agent.js"]
```

2. **Build and Push to ECR**:

```bash
# Build image
docker build -t bedrock-agent-ts .

# Tag and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag bedrock-agent-ts:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bedrock-agent-ts:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bedrock-agent-ts:latest
```

3. **Create ECS Task Definition and Service**

### Option 3: AWS EC2

1. **Launch EC2 Instance**
   - Choose Amazon Linux 2 or Ubuntu
   - Attach IAM role with Bedrock permissions

2. **Setup on EC2**:

```bash
# Install Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Clone and setup
git clone <your-repo>
cd bedrock-agentcore-ts
npm install
npm run build

# Run with PM2 for process management
npm install -g pm2
pm2 start dist/examples/simple-agent.js --name bedrock-agent
pm2 save
pm2 startup
```

### Option 4: Serverless Framework

1. **Install Serverless**:

```bash
npm install -g serverless
```

2. **Create `serverless.yml`**:

```yaml
service: bedrock-agent-ts

provider:
  name: aws
  runtime: nodejs18.x
  region: us-east-1
  environment:
    BEDROCK_AGENT_ID: ${env:BEDROCK_AGENT_ID}
    BEDROCK_AGENT_ALIAS_ID: ${env:BEDROCK_AGENT_ALIAS_ID}
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - bedrock:InvokeAgent
          Resource: '*'

functions:
  invoke:
    handler: dist/lambda.handler
    events:
      - http:
          path: invoke
          method: post

plugins:
  - serverless-plugin-typescript
```

3. **Deploy**:

```bash
serverless deploy
```

---

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Error**: `UnrecognizedClientException` or `InvalidSignatureException`

**Solution**:
- Verify AWS credentials are correctly configured
- Check IAM permissions include `bedrock:InvokeAgent`
- Ensure credentials haven't expired

```bash
# Test AWS credentials
aws sts get-caller-identity
```

#### 2. Agent Not Found

**Error**: `ResourceNotFoundException: Agent not found`

**Solution**:
- Verify `BEDROCK_AGENT_ID` is correct
- Ensure agent exists in the correct AWS region
- Check agent alias is created and active

```bash
# List available agents
aws bedrock-agent list-agents --region us-east-1
```

#### 3. Region Mismatch

**Error**: Agent not accessible

**Solution**:
- Ensure the region in your config matches where the agent was created
- Bedrock Agents may not be available in all regions

#### 4. Module Not Found

**Error**: `Cannot find module '@aws-sdk/client-bedrock-agent-runtime'`

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

#### 5. TypeScript Compilation Errors

**Solution**:
```bash
npm run clean
npm run build
```

### Enable Debugging

Set `enableTrace: true` to see detailed agent reasoning:

```typescript
const config: AgentConfig = {
  agentId: process.env.BEDROCK_AGENT_ID!,
  agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID!,
  region: 'us-east-1',
  enableTrace: true,  // Enable debugging
};
```

### Logging

Add detailed logging:

```typescript
const response = await agent.invoke({
  inputText: 'Your query',
});

console.log('Session ID:', response.sessionId);
console.log('Response:', response.completion);
if (response.trace) {
  console.log('Trace:', JSON.stringify(response.trace, null, 2));
}
```

---

## Best Practices

### 1. Security

- **Never commit credentials** to version control
- Use environment variables or AWS Secrets Manager
- Apply least-privilege IAM permissions
- Rotate credentials regularly
- Use VPC endpoints for private network access

### 2. Cost Optimization

- Monitor usage with AWS Cost Explorer
- Set up billing alerts
- Use appropriate instance sizes for deployments
- Cache responses when possible
- Implement request throttling

### 3. Performance

- Reuse agent instances across requests
- Use streaming for long responses
- Implement connection pooling
- Cache frequently requested data
- Use async/await properly

### 4. Error Handling

```typescript
try {
  const response = await agent.invoke({
    inputText: query,
  });
  return response;
} catch (error) {
  if (error.name === 'ThrottlingException') {
    // Implement exponential backoff
  } else if (error.name === 'ResourceNotFoundException') {
    // Handle missing agent
  } else {
    // Log and handle other errors
  }
  throw error;
}
```

### 5. Session Management

- Use meaningful session IDs for tracking
- Clean up sessions when conversations end
- Implement session timeouts
- Store session state externally for scalability

### 6. Monitoring

- Set up CloudWatch metrics
- Track response times
- Monitor error rates
- Set up alerts for failures
- Use AWS X-Ray for distributed tracing

---

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS SDK for JavaScript](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [AWS Bedrock Agents Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)

---

## Support

For issues and questions:
- Check the troubleshooting section above
- Review AWS Bedrock documentation
- Check AWS Service Health Dashboard
- Contact AWS Support for service-specific issues

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
