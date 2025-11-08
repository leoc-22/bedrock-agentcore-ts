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

### Run Examples

```bash
# Simple agent example
npm run dev

# Streaming example
npx ts-node src/examples/streaming-agent.ts

# Session state example
npx ts-node src/examples/session-state-agent.ts
```

## Project Structure

```
bedrock-agentcore-ts/
├── src/
│   ├── agent-runtime.ts      # Main agent runtime implementation
│   ├── types.ts               # TypeScript type definitions
│   ├── index.ts               # Public API exports
│   └── examples/
│       ├── simple-agent.ts    # Basic usage example
│       ├── streaming-agent.ts # Streaming responses example
│       └── session-state-agent.ts # Session management example
├── dist/                      # Compiled JavaScript output
├── DEPLOYMENT_GUIDE.md        # Comprehensive deployment guide
├── package.json
├── tsconfig.json
└── README.md
```

## Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Comprehensive guide for setting up AWS, local development, and production deployment
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

This project supports multiple deployment options:

- **AWS Lambda**: Serverless function invocation
- **AWS ECS/Fargate**: Containerized deployment
- **AWS EC2**: Traditional server deployment
- **Serverless Framework**: Infrastructure as code

See the [Deployment Guide](DEPLOYMENT_GUIDE.md) for detailed instructions.

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
