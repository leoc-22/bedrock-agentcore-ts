# Bedrock AgentCore TypeScript Provisioning

This repository shows how to define and prepare an [AWS Bedrock AgentCore](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) agent using TypeScript and the AWS SDK for JavaScript v3. Instead of invoking an existing agent, the scripts here create (or update) an agent definition, prepare the latest version, and point an alias at the freshly prepared build.

## What you get

- Environment validation with [`zod`](https://github.com/colinhacks/zod) and optional prompt files.
- A reusable helper that provisions the agent, waits for it to reach `PREPARED`, and synchronises a named alias.
- A tiny CLI for local development (`npm run dev`) that can be incorporated into CI/CD pipelines.
- A matching AWS CLI walkthrough in case you prefer to manage the agent without writing TypeScript.

## Project structure

```
.
├── .env.example          # Template for required environment variables
├── src
│   ├── agent-builder.ts  # Core provisioning logic
│   ├── cli.ts            # Minimal CLI wrapper
│   └── config.ts         # Environment loader and validation
├── package.json
├── tsconfig.json
└── README.md
```

## Prerequisites

- Node.js 18+ and npm.
- Access to the AWS account/region where the agent will live.
- An IAM role with permissions for Bedrock (the "agent resource role") that the agent can assume. The role must include the `bedrock:InvokeModel` actions for the target foundation model and any downstream services the agent uses.
- Local AWS credentials with permission to call the Bedrock Agent APIs (for running the CLI) or the equivalent AWS CLI commands.

## Configuration

1. Copy `.env.example` to `.env` and fill in the placeholders.

   ```bash
   cp .env.example .env
   ```

   Required values:

   | Variable | Description |
   |----------|-------------|
   | `AWS_REGION` | Region that hosts the Bedrock agent. |
   | `FOUNDATION_MODEL` | Model identifier, e.g. `anthropic.claude-3-haiku-20240307-v1:0`. |
   | `AGENT_NAME` | Friendly name for the agent definition. |
   | `AGENT_DESCRIPTION` | Human-readable description. |
   | `AGENT_ALIAS_NAME` | Alias to create/update (for example `dev`). |
   | `AGENT_ROLE_ARN` | IAM role ARN assumed by the agent when invoking actions. |
   | `AGENT_INSTRUCTION` or `AGENT_INSTRUCTION_FILE` | Either provide the prompt inline or point to a file with the instructions. |

   Optional variables:

   | Variable | Default | Description |
   |----------|---------|-------------|
   | `IDLE_SESSION_TTL` | `900` | TTL (seconds) for agent sessions. |
   | `GUARDRAIL_IDENTIFIER` / `GUARDRAIL_VERSION` | – | Guardrail to attach to the agent. Must be supplied together. |

   To maintain prompts separately, set `AGENT_INSTRUCTION_FILE` (relative paths are resolved from the repository root).

## Running the TypeScript deployer

Install dependencies and execute the CLI:

```bash
npm install
npm run dev
```

The CLI logs a short summary and prints the resulting identifiers:

```
Preparing agent "typescript-agentcore-sample" in us-east-1 (alias: dev)
Deployment complete:
{
  "agentId": "A1B2C3",
  "agentArn": "arn:aws:bedrock:us-east-1:123456789012:agent/A1B2C3",
  "agentVersion": "3",
  "aliasId": "TST",
  "aliasArn": "arn:aws:bedrock:us-east-1:123456789012:agent-alias/A1B2C3/TST",
  "definitionChanged": true
}
```

To inspect the parsed configuration without making API calls, run:

```bash
npm run dev -- show-config
```

## How the script works

`src/agent-builder.ts` performs the following steps:

1. Loads and validates the environment configuration.
2. Uses `ListAgents` + `GetAgent` to find an existing agent with the provided name.
3. Creates the agent if one does not exist, or updates the description, instructions, foundation model, guardrail, session TTL, and resource role when they differ.
4. Calls `PrepareAgent` to build a new version, then polls `GetAgent` until the status reaches `PREPARED` (or fails/timeouts after five minutes).
5. Creates or updates the requested alias so that it points at the prepared version.

The helper returns the agent and alias identifiers, along with a boolean indicating whether the definition changed during the run. You can embed `deployAgent()` inside CI jobs or higher-level deployment frameworks.

## AWS CLI deployment guide

The same workflow can be accomplished with pure AWS CLI commands. Replace placeholder values (agent name, description, role ARN, etc.) with your own.

1. **Create or update the agent definition**

   ```bash
   aws bedrock-agent create-agent \
     --agent-name "typescript-agentcore-sample" \
     --description "Sample agent created with the AWS SDK for JavaScript" \
     --agent-resource-role-arn arn:aws:iam::123456789012:role/BedrockAgentRole \
     --foundation-model anthropic.claude-3-haiku-20240307-v1:0 \
     --instruction "You are an automation expert that explains how to use AWS Bedrock AgentCore with TypeScript." \
     --idle-session-ttl-in-seconds 900
   ```

   If the agent already exists, call `update-agent` with the same parameters to apply changes:

   ```bash
   aws bedrock-agent update-agent \
     --agent-id A1B2C3 \
     --description "Sample agent created with the AWS SDK for JavaScript" \
     --agent-resource-role-arn arn:aws:iam::123456789012:role/BedrockAgentRole \
     --foundation-model anthropic.claude-3-haiku-20240307-v1:0 \
     --instruction file://prompt.txt \
     --idle-session-ttl-in-seconds 900
   ```

   *(You can pass inline strings or use `file://` to load the prompt.)*

2. **Check the agent status**

   ```bash
   aws bedrock-agent get-agent --agent-id A1B2C3
   ```

   Confirm the response reports `"agentStatus": "CREATED"` or `"agentStatus": "PREPARED"` before continuing.

3. **Prepare the agent**

   ```bash
   aws bedrock-agent prepare-agent --agent-id A1B2C3
   ```

   Poll until the agent reaches the `PREPARED` state:

   ```bash
   watch -n 5 'aws bedrock-agent get-agent --agent-id A1B2C3 --query agent.agentStatus'
   ```

4. **Create or update the alias**

   ```bash
   aws bedrock-agent create-agent-alias \
     --agent-id A1B2C3 \
     --agent-alias-name dev \
     --agent-version 3
   ```

   To retarget an existing alias, issue:

   ```bash
   aws bedrock-agent update-agent-alias \
     --agent-id A1B2C3 \
     --agent-alias-id TST \
     --agent-version 3
   ```

5. **Optional guardrail configuration**

   If you use guardrails, include the `--guardrail-identifier` and `--guardrail-version` flags in the `create-agent` or `update-agent` calls.

The CLI and the TypeScript helper both converge on the same outcome: an agent definition prepared against the target foundation model and exposed through a named alias.

## Troubleshooting tips

- Ensure the agent resource role trusts the `bedrock.amazonaws.com` service principal and includes permissions for any action groups or knowledge bases you reference.
- `PrepareAgent` operations are asynchronous; the helper waits up to five minutes, but you can adjust `timeoutMs` inside `waitForAgentPrepared` if your configuration routinely takes longer.
- The repository intentionally avoids invoking the runtime. Use the generated alias with Bedrock Agent Runtime clients or downstream applications once preparation completes.

## Testing

⚠️ Not run (network access is restricted in this environment, preventing `npm install` and subsequent builds).
