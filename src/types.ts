/**
 * Type definitions for Bedrock AgentCore Runtime
 */

export interface AgentConfig {
  agentId: string;
  agentAliasId: string;
  region?: string;
  sessionId?: string;
  enableTrace?: boolean;
}

export interface SessionState {
  sessionAttributes?: Record<string, string>;
  promptSessionAttributes?: Record<string, string>;
}

export interface InvokeAgentRequest {
  inputText: string;
  sessionState?: SessionState;
  endSession?: boolean;
}

export interface AgentResponse {
  completion: string;
  sessionId: string;
  trace?: any[];
  citations?: any[];
}

export interface StreamChunk {
  type: 'chunk' | 'trace' | 'metadata' | 'error';
  data: any;
}

export interface ToolConfig {
  name: string;
  description: string;
  parameters: Record<string, any>;
}

export interface AgentOptions {
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  stopSequences?: string[];
}
