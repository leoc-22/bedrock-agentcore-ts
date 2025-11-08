/**
 * Simple example of using Bedrock AgentCore Runtime
 */

import { BedrockAgentRuntime } from '../agent-runtime';
import { AgentConfig } from '../types';

async function main() {
  // Configure your agent
  const config: AgentConfig = {
    agentId: process.env.BEDROCK_AGENT_ID || 'YOUR_AGENT_ID',
    agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID || 'YOUR_AGENT_ALIAS_ID',
    region: process.env.AWS_REGION || 'us-east-1',
    enableTrace: true, // Enable to see agent reasoning traces
  };

  // Create an agent runtime instance
  const agent = new BedrockAgentRuntime(config);

  console.log('Bedrock Agent Runtime - Simple Example');
  console.log('======================================\n');
  console.log(`Session ID: ${agent.getSessionId()}\n`);

  try {
    // Invoke the agent with a simple query
    console.log('User: What is AWS Bedrock?');
    const response = await agent.invoke({
      inputText: 'What is AWS Bedrock?',
    });

    console.log(`\nAgent: ${response.completion}\n`);

    if (response.trace && response.trace.length > 0) {
      console.log('--- Traces ---');
      console.log(JSON.stringify(response.trace, null, 2));
    }

    // Follow-up question in the same session
    console.log('\nUser: Can you summarize that in one sentence?');
    const followUp = await agent.invoke({
      inputText: 'Can you summarize that in one sentence?',
    });

    console.log(`\nAgent: ${followUp.completion}\n`);

    // End the session
    await agent.endSession();
    console.log('Session ended successfully');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

// Run the example
if (require.main === module) {
  main();
}
