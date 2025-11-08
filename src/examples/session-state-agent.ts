/**
 * Example of using session state with Bedrock AgentCore Runtime
 */

import { BedrockAgentRuntime } from '../agent-runtime';
import { AgentConfig, SessionState } from '../types';

async function main() {
  // Configure your agent
  const config: AgentConfig = {
    agentId: process.env.BEDROCK_AGENT_ID || 'YOUR_AGENT_ID',
    agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID || 'YOUR_AGENT_ALIAS_ID',
    region: process.env.AWS_REGION || 'us-east-1',
    enableTrace: false,
  };

  // Create an agent runtime instance
  const agent = new BedrockAgentRuntime(config);

  console.log('Bedrock Agent Runtime - Session State Example');
  console.log('=============================================\n');
  console.log(`Session ID: ${agent.getSessionId()}\n`);

  try {
    // Define session attributes to maintain context
    const sessionState: SessionState = {
      sessionAttributes: {
        userId: 'user-12345',
        userName: 'John Doe',
        userRole: 'developer',
      },
      promptSessionAttributes: {
        context: 'technical-discussion',
        topic: 'aws-services',
      },
    };

    // First query with session state
    console.log('User: Hello! I need help with AWS services.');
    const response1 = await agent.invoke({
      inputText: 'Hello! I need help with AWS services.',
      sessionState,
    });

    console.log(`\nAgent: ${response1.completion}\n`);

    // Follow-up query maintaining session context
    console.log('User: What are the key benefits?');
    const response2 = await agent.invoke({
      inputText: 'What are the key benefits?',
      sessionState,
    });

    console.log(`\nAgent: ${response2.completion}\n`);

    // Update session state
    sessionState.sessionAttributes!.lastQuery = 'benefits';
    sessionState.promptSessionAttributes!.sentiment = 'positive';

    // Another follow-up with updated session state
    console.log('User: Can you recommend which service to start with?');
    const response3 = await agent.invoke({
      inputText: 'Can you recommend which service to start with?',
      sessionState,
    });

    console.log(`\nAgent: ${response3.completion}\n`);

    // Reset session for a new conversation
    console.log('\n--- Starting new session ---\n');
    agent.resetSession();
    console.log(`New Session ID: ${agent.getSessionId()}\n`);

    // Query without previous context
    console.log('User: What were we talking about?');
    const response4 = await agent.invoke({
      inputText: 'What were we talking about?',
    });

    console.log(`\nAgent: ${response4.completion}\n`);

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
