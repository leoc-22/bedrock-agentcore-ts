import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { config as loadEnv } from "dotenv";
import { z } from "zod";

loadEnv();

const envSchema = z
  .object({
    AWS_REGION: z.string().min(1, "AWS_REGION is required"),
    FOUNDATION_MODEL: z.string().min(1, "FOUNDATION_MODEL is required"),
    AGENT_NAME: z.string().min(1, "AGENT_NAME is required"),
    AGENT_DESCRIPTION: z.string().min(1, "AGENT_DESCRIPTION is required"),
    AGENT_ALIAS_NAME: z.string().min(1, "AGENT_ALIAS_NAME is required"),
    AGENT_ROLE_ARN: z.string().min(1, "AGENT_ROLE_ARN is required"),
    AGENT_INSTRUCTION: z.string().optional(),
    AGENT_INSTRUCTION_FILE: z.string().optional(),
    IDLE_SESSION_TTL: z.string().optional(),
    GUARDRAIL_IDENTIFIER: z.string().optional(),
    GUARDRAIL_VERSION: z.string().optional()
  })
  .superRefine((value, ctx) => {
    if (!value.AGENT_INSTRUCTION && !value.AGENT_INSTRUCTION_FILE) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["AGENT_INSTRUCTION"],
        message: "Provide AGENT_INSTRUCTION or AGENT_INSTRUCTION_FILE"
      });
    }

    const hasGuardrailId = Boolean(value.GUARDRAIL_IDENTIFIER);
    const hasGuardrailVersion = Boolean(value.GUARDRAIL_VERSION);
    if (hasGuardrailId !== hasGuardrailVersion) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["GUARDRAIL_IDENTIFIER"],
        message: "GUARDRAIL_IDENTIFIER and GUARDRAIL_VERSION must be provided together"
      });
    }
  });

export interface EnvConfig {
  region: string;
  foundationModel: string;
  agentName: string;
  agentDescription: string;
  agentAliasName: string;
  agentRoleArn: string;
  instruction: string;
  idleSessionTTLInSeconds: number;
  guardrailIdentifier?: string;
  guardrailVersion?: string;
}

let cachedConfig: EnvConfig | undefined;

function loadInstruction(value: z.infer<typeof envSchema>): string {
  if (value.AGENT_INSTRUCTION_FILE) {
    const filePath = resolve(process.cwd(), value.AGENT_INSTRUCTION_FILE);
    try {
      const contents = readFileSync(filePath, "utf-8");
      const trimmed = contents.trim();
      if (!trimmed) {
        throw new Error(`Instruction file at ${filePath} is empty`);
      }
      return trimmed;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      throw new Error(`Unable to read AGENT_INSTRUCTION_FILE: ${message}`);
    }
  }

  return value.AGENT_INSTRUCTION!.trim();
}

export function getConfig(): EnvConfig {
  if (!cachedConfig) {
    const parsed = envSchema.parse(process.env);
    const idleSessionTTL = parsed.IDLE_SESSION_TTL ? Number(parsed.IDLE_SESSION_TTL) : 900;

    if (!Number.isInteger(idleSessionTTL) || idleSessionTTL <= 0) {
      throw new Error("IDLE_SESSION_TTL must be a positive integer (seconds)");
    }

    cachedConfig = {
      region: parsed.AWS_REGION,
      foundationModel: parsed.FOUNDATION_MODEL,
      agentName: parsed.AGENT_NAME,
      agentDescription: parsed.AGENT_DESCRIPTION,
      agentAliasName: parsed.AGENT_ALIAS_NAME,
      agentRoleArn: parsed.AGENT_ROLE_ARN,
      instruction: loadInstruction(parsed),
      idleSessionTTLInSeconds: idleSessionTTL,
      guardrailIdentifier: parsed.GUARDRAIL_IDENTIFIER,
      guardrailVersion: parsed.GUARDRAIL_VERSION
    };
  }

  return cachedConfig;
}
