import {
  BedrockAgentClient,
  CreateAgentAliasCommand,
  CreateAgentCommand,
  GetAgentCommand,
  ListAgentAliasesCommand,
  ListAgentsCommand,
  PrepareAgentCommand,
  UpdateAgentAliasCommand,
  UpdateAgentCommand,
  type Agent,
  type AgentAliasSummary,
  type AgentSummary
} from "@aws-sdk/client-bedrock-agent";
import { getConfig, type EnvConfig } from "./config.js";

let cachedClient: BedrockAgentClient | undefined;

function getClient(): BedrockAgentClient {
  if (!cachedClient) {
    const { region } = getConfig();
    cachedClient = new BedrockAgentClient({ region });
  }
  return cachedClient;
}

async function paginateAgents(client: BedrockAgentClient): Promise<AgentSummary[]> {
  const summaries: AgentSummary[] = [];
  let nextToken: string | undefined;

  do {
    const response = await client.send(new ListAgentsCommand({ nextToken }));
    summaries.push(...(response.agentSummaries ?? []));
    nextToken = response.nextToken;
  } while (nextToken);

  return summaries;
}

async function findAgentByName(client: BedrockAgentClient, agentName: string): Promise<Agent | undefined> {
  const summaries = await paginateAgents(client);
  const summary = summaries.find(item => item.agentName === agentName);
  if (!summary?.agentId) {
    return undefined;
  }

  const { agent } = await client.send(new GetAgentCommand({ agentId: summary.agentId }));
  return agent;
}

async function paginateAliases(client: BedrockAgentClient, agentId: string): Promise<AgentAliasSummary[]> {
  const summaries: AgentAliasSummary[] = [];
  let nextToken: string | undefined;

  do {
    const response = await client.send(
      new ListAgentAliasesCommand({
        agentId,
        nextToken
      })
    );
    summaries.push(...(response.agentAliasSummaries ?? []));
    nextToken = response.nextToken;
  } while (nextToken);

  return summaries;
}

interface EnsureAgentResult {
  agent: Agent;
  changed: boolean;
}

async function ensureAgentDefinition(client: BedrockAgentClient, config: EnvConfig): Promise<EnsureAgentResult> {
  const existing = await findAgentByName(client, config.agentName);

  if (!existing?.agentId) {
    const response = await client.send(
      new CreateAgentCommand({
        agentName: config.agentName,
        agentResourceRoleArn: config.agentRoleArn,
        description: config.agentDescription,
        instruction: config.instruction,
        foundationModel: config.foundationModel,
        idleSessionTTLInSeconds: config.idleSessionTTLInSeconds,
        guardrailConfiguration: config.guardrailIdentifier
          ? {
              guardrailIdentifier: config.guardrailIdentifier,
              guardrailVersion: config.guardrailVersion
            }
          : undefined
      })
    );

    if (!response.agent) {
      throw new Error("CreateAgentCommand returned no agent payload");
    }

    return { agent: response.agent, changed: true };
  }

  const needsUpdate =
    existing.description !== config.agentDescription ||
    existing.foundationModel !== config.foundationModel ||
    existing.instruction !== config.instruction ||
    existing.idleSessionTTLInSeconds !== config.idleSessionTTLInSeconds ||
    existing.agentResourceRoleArn !== config.agentRoleArn ||
    (config.guardrailIdentifier &&
      (existing.guardrailConfiguration?.guardrailIdentifier !== config.guardrailIdentifier ||
        existing.guardrailConfiguration?.guardrailVersion !== config.guardrailVersion)) ||
    (!config.guardrailIdentifier && existing.guardrailConfiguration !== undefined);

  if (!needsUpdate) {
    return { agent: existing, changed: false };
  }

  await client.send(
    new UpdateAgentCommand({
      agentId: existing.agentId!,
      description: config.agentDescription,
      foundationModel: config.foundationModel,
      instruction: config.instruction,
      agentResourceRoleArn: config.agentRoleArn,
      idleSessionTTLInSeconds: config.idleSessionTTLInSeconds,
      guardrailConfiguration: config.guardrailIdentifier
        ? {
            guardrailIdentifier: config.guardrailIdentifier,
            guardrailVersion: config.guardrailVersion
          }
        : undefined
    })
  );

  const { agent } = await client.send(new GetAgentCommand({ agentId: existing.agentId! }));
  if (!agent) {
    throw new Error("Updated agent could not be retrieved");
  }

  return { agent, changed: true };
}

async function waitForAgentPrepared(client: BedrockAgentClient, agentId: string, timeoutMs = 5 * 60 * 1000): Promise<void> {
  const start = Date.now();
  const pollIntervalMs = 5000;

  while (Date.now() - start < timeoutMs) {
    const { agent } = await client.send(new GetAgentCommand({ agentId }));
    const status = agent?.agentStatus;

    if (status === "PREPARED") {
      return;
    }

    if (status === "FAILED") {
      throw new Error(`Agent ${agentId} failed to prepare`);
    }

    await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
  }

  throw new Error(`Timed out waiting for agent ${agentId} to reach PREPARED status`);
}

async function ensureAgentAlias(
  client: BedrockAgentClient,
  agentId: string,
  aliasName: string,
  agentVersion: string
): Promise<AgentAliasSummary> {
  const aliases = await paginateAliases(client, agentId);
  const alias = aliases.find(item => item.agentAliasName === aliasName);

  if (!alias?.agentAliasId) {
    const response = await client.send(
      new CreateAgentAliasCommand({
        agentId,
        agentAliasName: aliasName,
        agentVersion
      })
    );

    if (!response.agentAlias) {
      throw new Error("CreateAgentAliasCommand returned no alias payload");
    }

    return response.agentAlias;
  }

  if (alias.agentVersion === agentVersion) {
    return alias;
  }

  const response = await client.send(
    new UpdateAgentAliasCommand({
      agentId,
      agentAliasId: alias.agentAliasId,
      agentVersion
    })
  );

  if (!response.agentAlias) {
    throw new Error("UpdateAgentAliasCommand returned no alias payload");
  }

  return response.agentAlias;
}

export interface DeployAgentResult {
  agentId: string;
  agentArn?: string;
  agentVersion: string;
  aliasId: string;
  aliasArn?: string;
  definitionChanged: boolean;
}

export async function deployAgent(): Promise<DeployAgentResult> {
  const config = getConfig();
  const client = getClient();

  const { agent, changed } = await ensureAgentDefinition(client, config);
  const agentId = agent.agentId;

  if (!agentId) {
    throw new Error("Agent is missing an identifier");
  }

  const prepareResponse = await client.send(new PrepareAgentCommand({ agentId }));
  const agentVersion = prepareResponse.agentVersion;

  if (!agentVersion) {
    throw new Error("PrepareAgentCommand did not return an agentVersion");
  }

  await waitForAgentPrepared(client, agentId);
  const alias = await ensureAgentAlias(client, agentId, config.agentAliasName, agentVersion);

  return {
    agentId,
    agentArn: agent.agentArn,
    agentVersion,
    aliasId: alias.agentAliasId!,
    aliasArn: alias.agentAliasArn,
    definitionChanged: changed
  };
}

export function describeConfiguration(): EnvConfig {
  return getConfig();
}
