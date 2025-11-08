/**
 * Interactive CLI for testing Bedrock Agent locally
 *
 * This provides a real-time chat interface for testing your agent
 */

import * as readline from 'readline';
import { BedrockAgentRuntime } from '../agent-runtime';
import { AgentConfig } from '../types';

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  blue: '\x1b[34m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
};

class InteractiveCLI {
  private agent: BedrockAgentRuntime;
  private rl: readline.Interface;
  private conversationHistory: Array<{ role: string; message: string }> = [];

  constructor(config: AgentConfig) {
    this.agent = new BedrockAgentRuntime(config);

    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: `${colors.green}You: ${colors.reset}`,
    });
  }

  /**
   * Start the interactive CLI session
   */
  async start() {
    this.printWelcome();

    this.rl.on('line', async (input: string) => {
      const trimmedInput = input.trim();

      // Handle special commands
      if (trimmedInput.startsWith('/')) {
        await this.handleCommand(trimmedInput);
        this.rl.prompt();
        return;
      }

      // Ignore empty input
      if (!trimmedInput) {
        this.rl.prompt();
        return;
      }

      // Process user query
      await this.processQuery(trimmedInput);
      this.rl.prompt();
    });

    this.rl.on('close', () => {
      this.printGoodbye();
      process.exit(0);
    });

    this.rl.prompt();
  }

  /**
   * Print welcome message
   */
  private printWelcome() {
    console.log(`\n${colors.bright}${colors.cyan}═══════════════════════════════════════════════════════════${colors.reset}`);
    console.log(`${colors.bright}${colors.cyan}  AWS Bedrock Agent - Interactive CLI${colors.reset}`);
    console.log(`${colors.bright}${colors.cyan}═══════════════════════════════════════════════════════════${colors.reset}\n`);

    console.log(`${colors.gray}Session ID: ${this.agent.getSessionId()}${colors.reset}`);
    console.log(`${colors.gray}Region: ${process.env.AWS_REGION || 'us-east-1'}${colors.reset}\n`);

    console.log(`${colors.yellow}Commands:${colors.reset}`);
    console.log(`  ${colors.cyan}/help${colors.reset}      - Show available commands`);
    console.log(`  ${colors.cyan}/reset${colors.reset}     - Start a new session`);
    console.log(`  ${colors.cyan}/history${colors.reset}   - Show conversation history`);
    console.log(`  ${colors.cyan}/clear${colors.reset}     - Clear the screen`);
    console.log(`  ${colors.cyan}/stream${colors.reset}    - Toggle streaming mode`);
    console.log(`  ${colors.cyan}/exit${colors.reset}      - Exit the CLI`);
    console.log(`\n${colors.gray}Type your message and press Enter to chat with your agent.${colors.reset}\n`);
  }

  /**
   * Print goodbye message
   */
  private printGoodbye() {
    console.log(`\n${colors.cyan}Goodbye! Thanks for using Bedrock Agent CLI.${colors.reset}\n`);
  }

  /**
   * Process user query and get agent response
   */
  private async processQuery(query: string) {
    // Add to history
    this.conversationHistory.push({ role: 'user', message: query });

    try {
      // Show loading indicator
      process.stdout.write(`${colors.blue}Agent: ${colors.gray}thinking...${colors.reset}`);

      const response = await this.agent.invoke({
        inputText: query,
      });

      // Clear the loading indicator
      readline.clearLine(process.stdout, 0);
      readline.cursorTo(process.stdout, 0);

      // Display response
      console.log(`${colors.blue}Agent: ${colors.reset}${response.completion}\n`);

      // Add to history
      this.conversationHistory.push({
        role: 'agent',
        message: response.completion,
      });
    } catch (error: any) {
      // Clear the loading indicator
      readline.clearLine(process.stdout, 0);
      readline.cursorTo(process.stdout, 0);

      console.error(`${colors.red}Error: ${error.message}${colors.reset}\n`);

      if (error.name === 'ThrottlingException') {
        console.log(`${colors.yellow}Tip: You may be sending requests too quickly. Wait a moment and try again.${colors.reset}\n`);
      }
    }
  }

  /**
   * Handle special commands
   */
  private async handleCommand(command: string) {
    const cmd = command.toLowerCase().trim();

    switch (cmd) {
      case '/help':
        this.showHelp();
        break;

      case '/reset':
        this.agent.resetSession();
        this.conversationHistory = [];
        console.log(`${colors.green}✓ New session started${colors.reset}`);
        console.log(`${colors.gray}Session ID: ${this.agent.getSessionId()}${colors.reset}\n`);
        break;

      case '/history':
        this.showHistory();
        break;

      case '/clear':
        console.clear();
        this.printWelcome();
        break;

      case '/stream':
        console.log(`${colors.yellow}Streaming mode is not yet implemented in this CLI.${colors.reset}`);
        console.log(`${colors.gray}Use src/examples/streaming-agent.ts for streaming examples.${colors.reset}\n`);
        break;

      case '/exit':
      case '/quit':
        this.rl.close();
        break;

      default:
        console.log(`${colors.red}Unknown command: ${command}${colors.reset}`);
        console.log(`${colors.gray}Type /help to see available commands${colors.reset}\n`);
    }
  }

  /**
   * Show help message
   */
  private showHelp() {
    console.log(`\n${colors.bright}Available Commands:${colors.reset}\n`);
    console.log(`  ${colors.cyan}/help${colors.reset}      - Show this help message`);
    console.log(`  ${colors.cyan}/reset${colors.reset}     - Start a new session (clears conversation history)`);
    console.log(`  ${colors.cyan}/history${colors.reset}   - Display the conversation history`);
    console.log(`  ${colors.cyan}/clear${colors.reset}     - Clear the terminal screen`);
    console.log(`  ${colors.cyan}/stream${colors.reset}    - Toggle streaming mode (coming soon)`);
    console.log(`  ${colors.cyan}/exit${colors.reset}      - Exit the interactive CLI`);
    console.log(`\n${colors.bright}Tips:${colors.reset}`);
    console.log(`  - Press Ctrl+C or type /exit to quit`);
    console.log(`  - Use /reset to start fresh if the agent loses context`);
    console.log(`  - Multi-turn conversations maintain context automatically\n`);
  }

  /**
   * Show conversation history
   */
  private showHistory() {
    if (this.conversationHistory.length === 0) {
      console.log(`${colors.gray}No conversation history yet.${colors.reset}\n`);
      return;
    }

    console.log(`\n${colors.bright}Conversation History:${colors.reset}\n`);
    this.conversationHistory.forEach((entry, index) => {
      const color = entry.role === 'user' ? colors.green : colors.blue;
      const label = entry.role === 'user' ? 'You' : 'Agent';
      console.log(`${color}${label}:${colors.reset} ${entry.message}\n`);
    });
  }
}

/**
 * Main function to start the CLI
 */
async function main() {
  // Validate environment variables
  if (!process.env.BEDROCK_AGENT_ID || !process.env.BEDROCK_AGENT_ALIAS_ID) {
    console.error(`${colors.red}Error: Missing required environment variables${colors.reset}\n`);
    console.error('Please set the following in your .env file:');
    console.error('  - BEDROCK_AGENT_ID');
    console.error('  - BEDROCK_AGENT_ALIAS_ID');
    console.error('\nSee .env.example for reference.\n');
    process.exit(1);
  }

  // Configure agent
  const config: AgentConfig = {
    agentId: process.env.BEDROCK_AGENT_ID,
    agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID,
    region: process.env.AWS_REGION || 'us-east-1',
    enableTrace: process.env.ENABLE_TRACE === 'true',
  };

  // Start interactive CLI
  const cli = new InteractiveCLI(config);
  await cli.start();
}

// Handle Ctrl+C gracefully
process.on('SIGINT', () => {
  console.log(`\n\n${colors.cyan}Goodbye!${colors.reset}\n`);
  process.exit(0);
});

// Run the CLI
if (require.main === module) {
  main();
}
