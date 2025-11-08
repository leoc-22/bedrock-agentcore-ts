/**
 * Connection test script for AWS Bedrock Agent
 *
 * Run this script to verify your AWS credentials and agent configuration
 */

import { BedrockAgentRuntime } from './agent-runtime';
import { AgentConfig } from './types';

// Terminal colors
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
};

/**
 * Print a step message
 */
function printStep(step: number, message: string) {
  console.log(`\n${colors.cyan}[${step}]${colors.reset} ${message}...`);
}

/**
 * Print success message
 */
function printSuccess(message: string) {
  console.log(`${colors.green}✓${colors.reset} ${message}`);
}

/**
 * Print error message
 */
function printError(message: string) {
  console.log(`${colors.red}✗${colors.reset} ${message}`);
}

/**
 * Print info message
 */
function printInfo(message: string) {
  console.log(`${colors.gray}  ${message}${colors.reset}`);
}

/**
 * Main test function
 */
async function testConnection() {
  console.log('\n═══════════════════════════════════════════════════');
  console.log('  AWS Bedrock Agent - Connection Test');
  console.log('═══════════════════════════════════════════════════\n');

  // Step 1: Check environment variables
  printStep(1, 'Checking environment variables');

  const requiredVars = ['BEDROCK_AGENT_ID', 'BEDROCK_AGENT_ALIAS_ID'];
  const missingVars: string[] = [];

  for (const varName of requiredVars) {
    if (process.env[varName]) {
      printSuccess(`${varName} is set`);
      printInfo(`Value: ${process.env[varName]}`);
    } else {
      printError(`${varName} is not set`);
      missingVars.push(varName);
    }
  }

  if (missingVars.length > 0) {
    console.log(`\n${colors.red}Missing required environment variables!${colors.reset}`);
    console.log('\nPlease set the following in your .env file:');
    missingVars.forEach((v) => console.log(`  - ${v}`));
    console.log('\nSee .env.example for reference.\n');
    process.exit(1);
  }

  const region = process.env.AWS_REGION || 'us-east-1';
  printInfo(`AWS Region: ${region}`);

  // Step 2: Initialize agent
  printStep(2, 'Initializing Bedrock Agent Runtime');

  let agent: BedrockAgentRuntime;
  const config: AgentConfig = {
    agentId: process.env.BEDROCK_AGENT_ID!,
    agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID!,
    region,
    enableTrace: true,
  };

  try {
    agent = new BedrockAgentRuntime(config);
    printSuccess('Agent runtime initialized');
    printInfo(`Session ID: ${agent.getSessionId()}`);
  } catch (error: any) {
    printError('Failed to initialize agent runtime');
    console.error(`\n${colors.red}Error:${colors.reset}`, error.message);
    process.exit(1);
  }

  // Step 3: Test AWS credentials
  printStep(3, 'Testing AWS credentials');

  try {
    // Try to invoke the agent with a simple test
    printInfo('Sending test query to Bedrock...');

    const response = await agent.invoke({
      inputText: 'Hello, this is a connection test. Please respond with "Connection successful".',
    });

    printSuccess('AWS credentials are valid');
    printSuccess('Successfully connected to Bedrock Agent');

    // Step 4: Display test response
    printStep(4, 'Test Results');

    console.log(`\n${colors.cyan}Agent Response:${colors.reset}`);
    console.log(`  ${response.completion}\n`);

    printInfo(`Session ID: ${response.sessionId}`);

    if (response.trace && response.trace.length > 0) {
      printInfo(`Trace events captured: ${response.trace.length}`);
    }

    // Success summary
    console.log('\n═══════════════════════════════════════════════════');
    console.log(`${colors.green}✓ All tests passed!${colors.reset}`);
    console.log('═══════════════════════════════════════════════════');
    console.log('\nYour Bedrock Agent is ready to use!');
    console.log('\nNext steps:');
    console.log('  1. Run examples: npm run dev');
    console.log('  2. Interactive CLI: npx ts-node src/examples/interactive-cli.ts');
    console.log('  3. See LOCAL_TESTING.md for more testing options\n');

    process.exit(0);
  } catch (error: any) {
    printError('Connection test failed');

    console.log(`\n${colors.red}Error Details:${colors.reset}`);
    console.log(`  Name: ${error.name}`);
    console.log(`  Message: ${error.message}\n`);

    // Provide specific troubleshooting tips
    console.log(`${colors.yellow}Troubleshooting Tips:${colors.reset}\n`);

    if (error.name === 'UnrecognizedClientException') {
      console.log('❌ AWS credentials are invalid or not found');
      console.log('\nSolutions:');
      console.log('  1. Run: aws configure');
      console.log('  2. Verify: aws sts get-caller-identity');
      console.log('  3. Check ~/.aws/credentials file exists');
      console.log('  4. Set AWS_PROFILE if using a non-default profile\n');
    } else if (error.name === 'ResourceNotFoundException') {
      console.log('❌ Bedrock Agent not found');
      console.log('\nSolutions:');
      console.log('  1. Verify Agent ID and Alias ID in .env file');
      console.log('  2. Check the agent exists in the correct region');
      console.log('  3. Run: aws bedrock-agent list-agents --region ' + region);
      console.log('  4. Ensure agent is in "Prepared" or "Ready" state\n');
    } else if (error.name === 'AccessDeniedException') {
      console.log('❌ Insufficient IAM permissions');
      console.log('\nSolutions:');
      console.log('  1. Ensure your IAM user/role has bedrock:InvokeAgent permission');
      console.log('  2. Check IAM policy attached to your user/role');
      console.log('  3. Required permissions:');
      console.log('     - bedrock:InvokeAgent');
      console.log('     - bedrock:GetAgent');
      console.log('     - bedrock:ListAgents\n');
    } else if (error.name === 'ValidationException') {
      console.log('❌ Invalid request parameters');
      console.log('\nSolutions:');
      console.log('  1. Check Agent ID format (should be 10 characters)');
      console.log('  2. Check Alias ID format (should be 10 characters)');
      console.log('  3. Verify IDs in AWS Console\n');
    } else if (error.code === 'ENOTFOUND' || error.code === 'ETIMEDOUT') {
      console.log('❌ Network connectivity issue');
      console.log('\nSolutions:');
      console.log('  1. Check internet connection');
      console.log('  2. Verify region is correct');
      console.log('  3. Check firewall/proxy settings');
      console.log('  4. Try: ping bedrock-agent-runtime.' + region + '.amazonaws.com\n');
    } else {
      console.log('❌ Unexpected error occurred');
      console.log('\nSolutions:');
      console.log('  1. Check the error details above');
      console.log('  2. Review LOCAL_TESTING.md for more help');
      console.log('  3. Check AWS Service Health Dashboard');
      console.log('  4. Enable trace logging: ENABLE_TRACE=true in .env\n');
    }

    console.log('For more help, see: LOCAL_TESTING.md\n');
    process.exit(1);
  }
}

// Handle Ctrl+C
process.on('SIGINT', () => {
  console.log('\n\nTest interrupted by user.\n');
  process.exit(1);
});

// Run the test
if (require.main === module) {
  testConnection();
}

export { testConnection };
