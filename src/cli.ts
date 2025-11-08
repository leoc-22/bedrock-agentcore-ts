#!/usr/bin/env node
import process from "node:process";
import { describeConfiguration, deployAgent } from "./agent-builder.js";

async function main(): Promise<void> {
  const [, , command] = process.argv;

  if (command === "show-config") {
    const config = describeConfiguration();
    console.log("Loaded configuration:");
    console.log(JSON.stringify(config, null, 2));
    return;
  }

  const config = describeConfiguration();
  console.log(`Preparing agent "${config.agentName}" in ${config.region} (alias: ${config.agentAliasName})`);

  const result = await deployAgent();
  console.log("Deployment complete:");
  console.log(JSON.stringify(result, null, 2));
}

main().catch(error => {
  console.error("Agent deployment failed:", error);
  process.exitCode = 1;
});
