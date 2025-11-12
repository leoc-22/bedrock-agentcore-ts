#!/bin/bash
# Deployment helper script for AgentCore Runtime

set -e  # Exit on error

RUNTIME_NAME="business-scraper"
ENTRYPOINT="runtime_agent.py"
REGION="us-west-2"

echo "=========================================="
echo "Business Scraper Agent - Deployment Script"
echo "=========================================="
echo ""

# Check if agentcore CLI is installed
if ! command -v agentcore &> /dev/null; then
    echo "Error: agentcore CLI not found"
    echo "Install it with: pip install bedrock-agentcore-starter-toolkit"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS credentials not configured"
    echo "Run: aws configure"
    exit 1
fi

echo "✓ Prerequisites checked"
echo ""

# Function to show usage
show_usage() {
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  configure    - Configure AgentCore settings"
    echo "  deploy       - Deploy the agent to AgentCore Runtime"
    echo "  invoke       - Invoke the deployed agent"
    echo "  logs         - View agent logs"
    echo "  list         - List all runtimes"
    echo "  delete       - Delete the runtime"
    echo "  full         - Full deployment (configure + deploy)"
    echo ""
    echo "Example:"
    echo "  ./deploy.sh full"
    echo "  ./deploy.sh invoke"
}

# Parse command
COMMAND=${1:-help}

case $COMMAND in
    configure)
        echo "Configuring AgentCore..."
        agentcore configure
        echo "✓ Configuration complete"
        ;;

    deploy)
        echo "Deploying agent to AgentCore Runtime..."
        echo "Runtime name: $RUNTIME_NAME"
        echo "Entrypoint: $ENTRYPOINT"
        echo ""

        agentcore launch \
            --entrypoint $ENTRYPOINT \
            --runtime-name $RUNTIME_NAME

        echo ""
        echo "✓ Deployment complete!"
        echo ""
        echo "Next steps:"
        echo "  1. Test: ./deploy.sh invoke"
        echo "  2. View logs: ./deploy.sh logs"
        ;;

    invoke)
        echo "Invoking agent..."

        # Check if website URL is provided
        WEBSITE=${2:-"https://www.example.com.au"}

        echo "Website: $WEBSITE"
        echo ""

        agentcore invoke \
            --runtime-name $RUNTIME_NAME \
            --payload "{\"website\": \"$WEBSITE\"}"
        ;;

    stream)
        echo "Invoking agent with streaming..."

        WEBSITE=${2:-"https://www.example.com.au"}

        echo "Website: $WEBSITE"
        echo ""

        agentcore invoke \
            --runtime-name $RUNTIME_NAME \
            --entrypoint scrape_business_streaming \
            --payload "{\"website\": \"$WEBSITE\"}" \
            --stream
        ;;

    logs)
        echo "Viewing logs for $RUNTIME_NAME..."
        echo ""
        agentcore logs --runtime-name $RUNTIME_NAME
        ;;

    list)
        echo "Listing all runtimes..."
        echo ""
        agentcore list
        ;;

    delete)
        echo "Deleting runtime: $RUNTIME_NAME"
        read -p "Are you sure? (y/N): " confirm

        if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
            agentcore delete --runtime-name $RUNTIME_NAME
            echo "✓ Runtime deleted"
        else
            echo "Cancelled"
        fi
        ;;

    full)
        echo "Full deployment process..."
        echo ""

        # Configure
        echo "Step 1: Configuration"
        agentcore configure
        echo ""

        # Deploy
        echo "Step 2: Deployment"
        agentcore launch \
            --entrypoint $ENTRYPOINT \
            --runtime-name $RUNTIME_NAME
        echo ""

        # Test
        echo "Step 3: Testing"
        echo "Invoking with test website..."
        agentcore invoke \
            --runtime-name $RUNTIME_NAME \
            --payload '{"website": "https://www.example.com.au"}'

        echo ""
        echo "✓ Full deployment complete!"
        ;;

    help|--help|-h)
        show_usage
        ;;

    *)
        echo "Error: Unknown command '$COMMAND'"
        echo ""
        show_usage
        exit 1
        ;;
esac
