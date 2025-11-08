/**
 * AWS Bedrock AgentCore Runtime implementation in TypeScript
 */

import {
  BedrockAgentRuntimeClient,
  InvokeAgentCommand,
  InvokeAgentCommandInput,
  InvokeAgentCommandOutput,
} from '@aws-sdk/client-bedrock-agent-runtime';
import { fromEnv, fromIni } from '@aws-sdk/credential-providers';
import { AgentConfig, AgentResponse, InvokeAgentRequest, StreamChunk } from './types';

export class BedrockAgentRuntime {
  private client: BedrockAgentRuntimeClient;
  private config: AgentConfig;
  private sessionId: string;

  constructor(config: AgentConfig) {
    this.config = config;
    this.sessionId = config.sessionId || this.generateSessionId();

    // Initialize the Bedrock Agent Runtime client
    this.client = new BedrockAgentRuntimeClient({
      region: config.region || process.env.AWS_REGION || 'us-east-1',
      credentials: process.env.AWS_ACCESS_KEY_ID
        ? fromEnv()
        : fromIni({ profile: process.env.AWS_PROFILE }),
    });
  }

  /**
   * Generate a unique session ID
   */
  private generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }

  /**
   * Invoke the agent with a text prompt
   */
  async invoke(request: InvokeAgentRequest): Promise<AgentResponse> {
    const input: InvokeAgentCommandInput = {
      agentId: this.config.agentId,
      agentAliasId: this.config.agentAliasId,
      sessionId: this.sessionId,
      inputText: request.inputText,
      enableTrace: this.config.enableTrace || false,
      endSession: request.endSession || false,
    };

    if (request.sessionState) {
      input.sessionState = {
        sessionAttributes: request.sessionState.sessionAttributes,
        promptSessionAttributes: request.sessionState.promptSessionAttributes,
      };
    }

    try {
      const command = new InvokeAgentCommand(input);
      const response: InvokeAgentCommandOutput = await this.client.send(command);

      // Process the streaming response
      const result = await this.processResponse(response);
      return result;
    } catch (error) {
      console.error('Error invoking agent:', error);
      throw error;
    }
  }

  /**
   * Process the streaming response from the agent
   */
  private async processResponse(response: InvokeAgentCommandOutput): Promise<AgentResponse> {
    let completion = '';
    const traces: any[] = [];
    const citations: any[] = [];

    if (!response.completion) {
      throw new Error('No completion stream in response');
    }

    // Process the event stream
    for await (const event of response.completion) {
      if (event.chunk) {
        const chunkData = event.chunk.bytes;
        if (chunkData) {
          const text = new TextDecoder().decode(chunkData);
          completion += text;
        }
      }

      if (event.trace && this.config.enableTrace) {
        traces.push(event.trace);
      }

      if ('metadata' in event && event.metadata) {
        // Handle metadata events
        console.log('Metadata:', event.metadata);
      }

      if ('citation' in event && event.citation) {
        citations.push(event.citation);
      }
    }

    return {
      completion: completion.trim(),
      sessionId: this.sessionId,
      trace: traces.length > 0 ? traces : undefined,
      citations: citations.length > 0 ? citations : undefined,
    };
  }

  /**
   * Invoke the agent with streaming response
   */
  async *invokeStream(request: InvokeAgentRequest): AsyncGenerator<StreamChunk, void, unknown> {
    const input: InvokeAgentCommandInput = {
      agentId: this.config.agentId,
      agentAliasId: this.config.agentAliasId,
      sessionId: this.sessionId,
      inputText: request.inputText,
      enableTrace: this.config.enableTrace || false,
      endSession: request.endSession || false,
    };

    if (request.sessionState) {
      input.sessionState = {
        sessionAttributes: request.sessionState.sessionAttributes,
        promptSessionAttributes: request.sessionState.promptSessionAttributes,
      };
    }

    try {
      const command = new InvokeAgentCommand(input);
      const response: InvokeAgentCommandOutput = await this.client.send(command);

      if (!response.completion) {
        throw new Error('No completion stream in response');
      }

      // Yield streaming events
      for await (const event of response.completion) {
        if (event.chunk) {
          const chunkData = event.chunk.bytes;
          if (chunkData) {
            const text = new TextDecoder().decode(chunkData);
            yield {
              type: 'chunk',
              data: text,
            };
          }
        }

        if (event.trace && this.config.enableTrace) {
          yield {
            type: 'trace',
            data: event.trace,
          };
        }

        if ('metadata' in event && event.metadata) {
          yield {
            type: 'metadata',
            data: event.metadata,
          };
        }
      }
    } catch (error) {
      yield {
        type: 'error',
        data: error,
      };
      throw error;
    }
  }

  /**
   * Get the current session ID
   */
  getSessionId(): string {
    return this.sessionId;
  }

  /**
   * Reset the session (generates a new session ID)
   */
  resetSession(): void {
    this.sessionId = this.generateSessionId();
  }

  /**
   * End the current session
   */
  async endSession(): Promise<AgentResponse> {
    return this.invoke({
      inputText: '',
      endSession: true,
    });
  }
}
