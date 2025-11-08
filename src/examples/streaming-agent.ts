/**
 * Example of streaming responses from Bedrock AgentCore Runtime
 */

import { BedrockAgentRuntime } from '../agent-runtime';
import { AgentConfig } from '../types';

async function main() {
  // Configure your agent
  const config: AgentConfig = {
    agentId: process.env.BEDROCK_AGENT_ID || 'YOUR_AGENT_ID',
    agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID || 'YOUR_AGENT_ALIAS_ID',
    region: process.env.AWS_REGION || 'us-east-1',
    enableTrace: false, // Disable traces for cleaner streaming output
  };

  // Create an agent runtime instance
  const agent = new BedrockAgentRuntime(config);

  console.log('Bedrock Agent Runtime - Streaming Example');
  console.log('=========================================\n');
  console.log(`Session ID: ${agent.getSessionId()}\n`);

  try {
    const query = 'Tell me a short story about AI and cloud computing';
    console.log(`User: ${query}\n`);
    console.log('Agent: ');

    // Stream the response
    for await (const chunk of agent.invokeStream({
      inputText: query,
    })) {
      if (chunk.type === 'chunk') {
        // Print chunks as they arrive for real-time output
        process.stdout.write(chunk.data);
      } else if (chunk.type === 'trace') {
        // Handle trace data if needed
        console.log('\n[Trace]', chunk.data);
      } else if (chunk.type === 'metadata') {
        // Handle metadata if needed
        console.log('\n[Metadata]', chunk.data);
      } else if (chunk.type === 'error') {
        console.error('\n[Error]', chunk.data);
      }
    }

    console.log('\n\nStreaming completed successfully');

    // End the session
    await agent.endSession();
  } catch (error) {
    console.error('\nError:', error);
    process.exit(1);
  }
}

// Run the example
if (require.main === module) {
  main();
}
