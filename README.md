# bedrock-agentcore-ts

TypeScript implementation for AWS Bedrock AgentCore Runtime - Build powerful AI agents using TypeScript instead of the first-class supported Python frameworks.

## Overview

This project provides a complete TypeScript SDK for AWS Bedrock AgentCore Runtime, enabling you to:

- Create and manage AI agents using TypeScript
- Stream responses in real-time
- Maintain conversational context with session management
- Integrate with AWS Bedrock's powerful AI capabilities
- Deploy to various AWS services (Lambda, ECS, EC2)

## Features

- **Full TypeScript Support**: Type-safe agent interactions with comprehensive type definitions
- **Streaming Responses**: Real-time streaming for better user experience
- **Session Management**: Maintain context across multiple interactions
- **AWS Integration**: Seamless integration with AWS credentials and services
- **Multiple Examples**: Production-ready examples for common use cases
- **Comprehensive Documentation**: Detailed deployment and usage guides

## Quick Start

### Prerequisites

- Node.js 22.x or higher
- AWS Account with Bedrock access
- AWS credentials configured

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd bedrock-agentcore-ts

# Install dependencies
npm install

# Build the project
npm run build
```

### Configuration

1. Create a `.env` file:

```bash
BEDROCK_AGENT_ID=your_agent_id
BEDROCK_AGENT_ALIAS_ID=your_agent_alias_id
AWS_REGION=us-east-1
```

2. Ensure AWS credentials are configured (via environment variables or `~/.aws/credentials`)

### Basic Usage

```typescript
import { BedrockAgentRuntime } from './src';

const agent = new BedrockAgentRuntime({
  agentId: process.env.BEDROCK_AGENT_ID!,
  agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID!,
  region: 'us-east-1',
});

const response = await agent.invoke({
  inputText: 'What is AWS Bedrock?',
});

console.log(response.completion);
```

### Test Your Setup

```bash
# Test AWS connection and credentials
npm test
```

### Run Examples

```bash
# Simple agent example
npm run dev

# Interactive chat CLI (recommended for local testing)
npm run chat

# Streaming example
npm run stream

# Session state example
npm run session
```

## Project Structure

```
bedrock-agentcore-ts/
├── src/
│   ├── agent-runtime.ts       # Main agent runtime implementation
│   ├── types.ts               # TypeScript type definitions
│   ├── index.ts               # Public API exports
│   ├── test-connection.ts     # Connection test script
│   └── examples/
│       ├── simple-agent.ts           # Basic usage example
│       ├── streaming-agent.ts        # Streaming responses example
│       ├── session-state-agent.ts    # Session management example
│       └── interactive-cli.ts        # Interactive chat CLI
├── terraform/                 # Infrastructure as Code
│   ├── main.tf                # Main Terraform configuration
│   ├── variables.tf           # Variable definitions
│   ├── outputs.tf             # Output values
│   ├── environments/          # Environment-specific configs
│   │   ├── dev.tfvars
│   │   └── prod.tfvars
│   └── README.md              # Terraform documentation
├── dist/                      # Compiled JavaScript output
├── LOCAL_TESTING.md           # Local testing guide
├── DEPLOYMENT_GUIDE.md        # Manual deployment guide
├── package.json
├── tsconfig.json
└── README.md
```

## Local Testing

Testing your agent locally while connecting to AWS Bedrock is straightforward:

### 1. Quick Connection Test

Verify your AWS credentials and agent configuration:

```bash
npm test
```

This will:

- Check environment variables
- Verify AWS credentials
- Test connection to your Bedrock agent
- Display helpful error messages if something is wrong

### 2. Interactive Chat CLI

The best way to test locally is using the interactive CLI:

```bash
npm run chat
```

Features:

- Real-time chat interface
- Conversation history
- Session management
- Built-in commands (`/help`, `/reset`, `/history`, etc.)

### 3. Available npm Scripts

```bash
npm test      # Connection test
npm run dev   # Simple agent example
npm run chat  # Interactive CLI (recommended)
npm run stream # Streaming example
npm run session # Session state example
```

### 4. Detailed Testing Guide

For comprehensive local testing instructions, see **[LOCAL_TESTING.md](LOCAL_TESTING.md)**, which covers:

- AWS credential setup
- Environment configuration
- Common testing scenarios
- Troubleshooting tips
- Development workflows

## Documentation

- **[Terraform Infrastructure Guide](terraform/README.md)**: Complete Terraform documentation for infrastructure as code deployment (recommended)
- **[Local Testing Guide](LOCAL_TESTING.md)**: Complete guide for testing locally while connecting to AWS Bedrock
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Comprehensive guide for manual deployment to AWS services
- **[Examples](src/examples/)**: Working examples for common use cases

## API Reference

### BedrockAgentRuntime

Main class for interacting with AWS Bedrock agents.

#### Constructor

```typescript
new BedrockAgentRuntime(config: AgentConfig)
```

#### Methods

- `invoke(request: InvokeAgentRequest): Promise<AgentResponse>` - Invoke agent with a query
- `invokeStream(request: InvokeAgentRequest): AsyncGenerator<StreamChunk>` - Stream responses
- `getSessionId(): string` - Get current session ID
- `resetSession(): void` - Start a new session
- `endSession(): Promise<AgentResponse>` - End the current session

### Types

```typescript
interface AgentConfig {
  agentId: string;
  agentAliasId: string;
  region?: string;
  sessionId?: string;
  enableTrace?: boolean;
}

interface InvokeAgentRequest {
  inputText: string;
  sessionState?: SessionState;
  endSession?: boolean;
}

interface AgentResponse {
  completion: string;
  sessionId: string;
  trace?: any[];
  citations?: any[];
}
```

## Deployment

### Infrastructure as Code with Terraform (Recommended)

Deploy your Bedrock Agent infrastructure with zero click-ops:

```bash
cd terraform
terraform init
terraform apply
```

The Terraform configuration deploys:

- ✅ Bedrock Agent with foundation model
- ✅ Agent Alias for environment management
- ✅ IAM roles and policies
- ✅ CloudWatch log groups
- ✅ Automatic agent preparation

**Quick Start:**

```bash
# 1. Create your configuration
cd terraform
cp terraform.tfvars.example terraform.tfvars

# 2. Edit terraform.tfvars with your preferences
# 3. Deploy
terraform init
terraform apply

# 4. Get your agent IDs
terraform output -raw env_file_content >> ../.env

# 5. Test your agent
cd ..
npm test
```

See **[terraform/README.md](terraform/README.md)** for complete Terraform documentation including:

- Multiple environment management (dev/staging/prod)
- Remote state configuration
- Advanced customization
- CI/CD integration

### Manual Deployment Options

This project also supports traditional deployment methods:

- **AWS Lambda**: Serverless function invocation
- **AWS ECS/Fargate**: Containerized deployment
- **AWS EC2**: Traditional server deployment
- **Serverless Framework**: Infrastructure as code

See the [Deployment Guide](DEPLOYMENT_GUIDE.md) for manual deployment instructions.

## Examples

### Simple Query

```typescript
const response = await agent.invoke({
  inputText: 'What is AWS Bedrock?',
});
console.log(response.completion);
```

### Streaming Response

```typescript
for await (const chunk of agent.invokeStream({ inputText: 'Tell me a story' })) {
  if (chunk.type === 'chunk') {
    process.stdout.write(chunk.data);
  }
}
```

### With Session State

```typescript
const response = await agent.invoke({
  inputText: 'Hello!',
  sessionState: {
    sessionAttributes: {
      userId: 'user-123',
      userName: 'John',
    },
  },
});
```

## Best Practices

1. **Reuse agent instances** across requests to avoid repeated initialization
2. **Use streaming** for long-form content to improve user experience
3. **Implement error handling** for network and service errors
4. **Monitor costs** by tracking API usage
5. **Use session management** for conversational contexts
6. **Enable traces** during development for debugging

## Troubleshooting

### Common Issues

- **Authentication errors**: Verify AWS credentials are properly configured
- **Agent not found**: Check agent ID and region are correct
- **Module not found**: Run `npm install` to install dependencies
- **Build errors**: Run `npm run clean && npm run build`

See [Deployment Guide - Troubleshooting](DEPLOYMENT_GUIDE.md#troubleshooting) for more details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Bedrock Agents Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [AWS SDK for JavaScript v3](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

## Support

For questions and support:

- Check the [Deployment Guide](DEPLOYMENT_GUIDE.md)
- Review [Examples](src/examples/)
- Open an issue on GitHub
