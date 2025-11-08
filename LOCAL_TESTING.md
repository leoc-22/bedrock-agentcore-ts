# Local Testing Guide

This guide walks you through testing your AWS Bedrock AgentCore TypeScript implementation locally while connecting to AWS Bedrock.

## Prerequisites

Before you start local testing:

1. ✅ AWS Bedrock Agent created and configured in AWS Console
2. ✅ Agent ID and Alias ID noted
3. ✅ AWS credentials configured
4. ✅ Node.js 22+ installed
5. ✅ Project dependencies installed

---

## Step 1: Set Up AWS Credentials

### Option A: Using AWS CLI Profile (Recommended for Local Testing)

1. **Install AWS CLI** (if not already installed):
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download from https://aws.amazon.com/cli/
```

2. **Configure AWS CLI**:
```bash
aws configure

# You'll be prompted for:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region name: us-east-1
# Default output format: json
```

3. **Verify configuration**:
```bash
# Test credentials
aws sts get-caller-identity

# Should output your account details:
# {
#     "UserId": "AIDAI...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-user"
# }

# Test Bedrock access
aws bedrock-agent list-agents --region us-east-1
```

### Option B: Using Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_REGION=us-east-1
```

### Option C: Using AWS SSO (For Organizations)

```bash
aws configure sso

# Follow the prompts to configure SSO
aws sso login --profile your-profile-name
```

---

## Step 2: Configure Environment Variables

1. **Copy the example environment file**:
```bash
cp .env.example .env
```

2. **Edit `.env` file** with your agent details:
```bash
# Required: Your Bedrock Agent configuration
BEDROCK_AGENT_ID=XXXXXXXXXX
BEDROCK_AGENT_ALIAS_ID=YYYYYYYYYY
AWS_REGION=us-east-1

# Optional: Specify AWS profile (if not using default)
# AWS_PROFILE=your-profile-name

# Optional: Enable trace for debugging
# ENABLE_TRACE=true
```

3. **Find your Agent ID and Alias ID**:

   **Via AWS Console:**
   - Go to AWS Console → Amazon Bedrock → Agents
   - Click on your agent
   - **Agent ID**: Found at the top of the agent details page
   - **Alias ID**: Go to "Aliases" tab → Click on your alias

   **Via AWS CLI:**
   ```bash
   # List all agents
   aws bedrock-agent list-agents --region us-east-1

   # Get agent details (replace YOUR_AGENT_ID)
   aws bedrock-agent get-agent --agent-id YOUR_AGENT_ID --region us-east-1

   # List agent aliases
   aws bedrock-agent list-agent-aliases --agent-id YOUR_AGENT_ID --region us-east-1
   ```

---

## Step 3: Install Dependencies

```bash
# Install all dependencies
npm install

# Build the TypeScript code
npm run build
```

---

## Step 4: Test Connection to Bedrock

### Quick Connection Test

Create a simple test file to verify connectivity:

```bash
# Create a test script
cat > test-connection.ts << 'EOF'
import { BedrockAgentRuntime } from './src';

async function testConnection() {
  console.log('Testing AWS Bedrock connection...\n');

  // Check environment variables
  if (!process.env.BEDROCK_AGENT_ID || !process.env.BEDROCK_AGENT_ALIAS_ID) {
    console.error('❌ Error: BEDROCK_AGENT_ID and BEDROCK_AGENT_ALIAS_ID must be set in .env');
    process.exit(1);
  }

  try {
    const agent = new BedrockAgentRuntime({
      agentId: process.env.BEDROCK_AGENT_ID!,
      agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID!,
      region: process.env.AWS_REGION || 'us-east-1',
      enableTrace: true,
    });

    console.log('✓ Agent initialized');
    console.log(`  Agent ID: ${process.env.BEDROCK_AGENT_ID}`);
    console.log(`  Alias ID: ${process.env.BEDROCK_AGENT_ALIAS_ID}`);
    console.log(`  Region: ${process.env.AWS_REGION || 'us-east-1'}\n`);

    console.log('Sending test query...\n');

    const response = await agent.invoke({
      inputText: 'Hello, can you hear me?',
    });

    console.log('✅ Success! Received response from Bedrock:\n');
    console.log(response.completion);
    console.log(`\nSession ID: ${response.sessionId}`);

  } catch (error: any) {
    console.error('❌ Error connecting to Bedrock:\n');
    console.error(error.message);

    if (error.name === 'UnrecognizedClientException') {
      console.error('\nTip: Check your AWS credentials are valid');
    } else if (error.name === 'ResourceNotFoundException') {
      console.error('\nTip: Verify your Agent ID and Alias ID are correct');
    } else if (error.name === 'AccessDeniedException') {
      console.error('\nTip: Ensure your IAM user/role has bedrock:InvokeAgent permission');
    }

    process.exit(1);
  }
}

testConnection();
EOF

# Run the test
npx ts-node test-connection.ts
```

---

## Step 5: Run the Examples

### Example 1: Simple Agent

```bash
# Run with ts-node (development)
npm run dev

# Or run compiled version
npm run build
npm start
```

### Example 2: Streaming Responses

```bash
npx ts-node src/examples/streaming-agent.ts
```

### Example 3: Session State Management

```bash
npx ts-node src/examples/session-state-agent.ts
```

---

## Step 6: Interactive Local Testing

For more interactive testing, I recommend creating an interactive CLI:

```bash
npx ts-node src/examples/interactive-cli.ts
```

This will start an interactive session where you can chat with your agent in real-time.

---

## Common Testing Scenarios

### Test 1: Simple Query/Response

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

### Test 2: Multi-turn Conversation

```typescript
// First message
const response1 = await agent.invoke({
  inputText: 'Tell me about AWS Lambda',
});
console.log('Agent:', response1.completion);

// Follow-up (maintains context)
const response2 = await agent.invoke({
  inputText: 'What are the pricing options?',
});
console.log('Agent:', response2.completion);
```

### Test 3: With Session Attributes

```typescript
const response = await agent.invoke({
  inputText: 'Hello!',
  sessionState: {
    sessionAttributes: {
      userId: 'test-user-123',
      userRole: 'developer',
    },
  },
});
```

### Test 4: Streaming Response

```typescript
console.log('Agent: ');
for await (const chunk of agent.invokeStream({
  inputText: 'Explain cloud computing',
})) {
  if (chunk.type === 'chunk') {
    process.stdout.write(chunk.data);
  }
}
console.log('\n');
```

### Test 5: With Debugging (Traces)

```typescript
const agent = new BedrockAgentRuntime({
  agentId: process.env.BEDROCK_AGENT_ID!,
  agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID!,
  region: 'us-east-1',
  enableTrace: true,  // Enable trace logs
});

const response = await agent.invoke({
  inputText: 'Your question',
});

// View agent reasoning traces
if (response.trace) {
  console.log('\n--- Agent Traces ---');
  console.log(JSON.stringify(response.trace, null, 2));
}
```

---

## Troubleshooting Local Testing

### Issue 1: "UnrecognizedClientException"

**Problem:** AWS credentials are invalid or not found.

**Solution:**
```bash
# Verify credentials are set
aws sts get-caller-identity

# If using profile, ensure it's set
export AWS_PROFILE=your-profile-name

# Or reconfigure AWS CLI
aws configure
```

### Issue 2: "ResourceNotFoundException: Agent not found"

**Problem:** Agent ID or Alias ID is incorrect, or agent is in a different region.

**Solution:**
```bash
# Verify agent exists
aws bedrock-agent get-agent --agent-id YOUR_AGENT_ID --region us-east-1

# List all agents in region
aws bedrock-agent list-agents --region us-east-1

# Double-check your .env file has correct IDs
cat .env
```

### Issue 3: "AccessDeniedException"

**Problem:** Your IAM user/role lacks permissions.

**Solution:**
```bash
# Check current user's permissions
aws iam get-user

# Required IAM policy (attach to your user/role):
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

### Issue 4: Connection Timeout

**Problem:** Network issues or region mismatch.

**Solution:**
```bash
# Check region matches where agent was created
# Update .env:
AWS_REGION=us-east-1  # or your agent's region

# Test network connectivity
ping bedrock-agent-runtime.us-east-1.amazonaws.com
```

### Issue 5: Module Not Found Errors

**Problem:** Dependencies not installed or build needed.

**Solution:**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Rebuild TypeScript
npm run build
```

---

## Development Workflow

### Recommended Workflow for Local Testing

1. **Start with simple test**:
   ```bash
   npx ts-node test-connection.ts
   ```

2. **Test specific features**:
   ```bash
   npx ts-node src/examples/simple-agent.ts
   ```

3. **Iterate and develop**:
   - Make code changes in `src/`
   - Test immediately with `ts-node`
   - No need to rebuild for development

4. **Final testing**:
   ```bash
   npm run build
   npm start
   ```

### Hot Reload Development

For faster development with auto-reload:

```bash
# Install nodemon
npm install -g nodemon

# Run with auto-reload
nodemon --watch src --exec "npx ts-node src/examples/simple-agent.ts"
```

---

## Testing Best Practices

### 1. Use Environment-Specific Aliases

Create different agent aliases for different environments:
- `dev` - For local development
- `test` - For testing
- `prod` - For production

Update `.env` to use the `dev` alias for local testing.

### 2. Enable Traces During Development

```typescript
const agent = new BedrockAgentRuntime({
  agentId: process.env.BEDROCK_AGENT_ID!,
  agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID!,
  region: 'us-east-1',
  enableTrace: process.env.NODE_ENV === 'development',
});
```

### 3. Use Different Sessions for Different Tests

```typescript
// Create fresh session for each test
agent.resetSession();
```

### 4. Log Requests and Responses

```typescript
const query = 'Your question';
console.log(`[${new Date().toISOString()}] Query:`, query);

const response = await agent.invoke({ inputText: query });

console.log(`[${new Date().toISOString()}] Response:`, response.completion);
console.log('Session ID:', response.sessionId);
```

### 5. Monitor Costs

Local testing uses real AWS resources and incurs costs:
- Set up AWS billing alerts
- Use CloudWatch to monitor usage
- Consider using smaller/cheaper models during development

---

## Next Steps

After successful local testing:

1. **Write Unit Tests**: Add Jest or Mocha tests
2. **Set Up CI/CD**: Automate testing in your pipeline
3. **Deploy to Dev Environment**: Test in a real cloud environment
4. **Monitor and Optimize**: Use CloudWatch metrics

---

## Additional Resources

- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [Bedrock Agent Runtime API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_Operations_Agents_for_Amazon_Bedrock_Runtime.html)
