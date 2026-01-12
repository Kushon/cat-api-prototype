#!/bin/bash

# Helm Chart Deployment Script for Cat API
# This script provides convenient commands for managing the Cat API Helm chart

set -e

CHART_PATH="./cat-api-chart"
RELEASE_NAME="${RELEASE_NAME:-cat-api-release}"
NAMESPACE="${NAMESPACE:-cat-api-ns}"
VALUES_FILE="${VALUES_FILE:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_usage() {
    cat << EOF
Usage: ./deploy.sh <command> [options]

Commands:
    install         Install the Helm chart
    upgrade         Upgrade the Helm chart
    uninstall       Uninstall the Helm chart
    dry-run         Test installation without applying changes
    lint            Lint the Helm chart
    values          Show computed values
    status          Show release status
    logs-app        Show application logs
    logs-db         Show database logs
    help            Show this help message

Options:
    -n, --namespace NAMESPACE     Kubernetes namespace (default: $NAMESPACE)
    -r, --release RELEASE_NAME    Release name (default: $RELEASE_NAME)
    -f, --values VALUES_FILE      Custom values file
    -h, --help                    Show this help message

Examples:
    ./deploy.sh install
    ./deploy.sh install -f examples/values-production.yaml
    ./deploy.sh upgrade -n production
    ./deploy.sh dry-run --values ./custom-values.yaml
    ./deploy.sh logs-app -n cat-api-ns

EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -r|--release)
                RELEASE_NAME="$2"
                shift 2
                ;;
            -f|--values)
                VALUES_FILE="$2"
                shift 2
                ;;
            -h|--help)
                print_usage
                exit 0
                ;;
            *)
                shift
                ;;
        esac
    done
}

check_dependencies() {
    if ! command -v helm &> /dev/null; then
        echo -e "${RED}Error: helm is not installed${NC}"
        exit 1
    fi
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: kubectl is not installed${NC}"
        exit 1
    fi
}

build_helm_command() {
    local cmd="helm $1 $RELEASE_NAME $CHART_PATH"
    cmd="$cmd --namespace $NAMESPACE --create-namespace"
    if [ -n "$VALUES_FILE" ]; then
        cmd="$cmd --values $VALUES_FILE"
    fi
    echo "$cmd"
}

cmd_install() {
    parse_args "$@"
    echo -e "${YELLOW}Installing Helm chart...${NC}"
    cmd=$(build_helm_command "install")
    echo -e "${GREEN}Running: $cmd${NC}"
    eval "$cmd"
    echo -e "${GREEN}Installation complete!${NC}"
    echo -e "\n${YELLOW}Next steps:${NC}"
    echo "1. Check deployment status: kubectl rollout status deployment/$RELEASE_NAME -n $NAMESPACE"
    echo "2. View logs: kubectl logs deployment/$RELEASE_NAME -n $NAMESPACE -f"
}

cmd_upgrade() {
    parse_args "$@"
    echo -e "${YELLOW}Upgrading Helm chart...${NC}"
    cmd=$(build_helm_command "upgrade")
    echo -e "${GREEN}Running: $cmd${NC}"
    eval "$cmd"
    echo -e "${GREEN}Upgrade complete!${NC}"
}

cmd_uninstall() {
    parse_args "$@"
    echo -e "${RED}Uninstalling Helm chart...${NC}"
    helm uninstall "$RELEASE_NAME" --namespace "$NAMESPACE" || true
    echo -e "${GREEN}Uninstallation complete!${NC}"
}

cmd_dry_run() {
    parse_args "$@"
    echo -e "${YELLOW}Running dry-run test...${NC}"
    cmd=$(build_helm_command "install")
    cmd="$cmd --dry-run=client"
    echo -e "${GREEN}Running: $cmd${NC}"
    echo ""
    eval "$cmd"
}

cmd_lint() {
    parse_args "$@"
    echo -e "${YELLOW}Linting Helm chart...${NC}"
    helm lint "$CHART_PATH" --strict
    echo -e "${GREEN}Lint passed!${NC}"
}

cmd_values() {
    parse_args "$@"
    echo -e "${YELLOW}Computed values:${NC}"
    cmd=$(build_helm_command "show values")
    eval "$cmd"
}

cmd_status() {
    parse_args "$@"
    echo -e "${YELLOW}Release Status:${NC}"
    helm status "$RELEASE_NAME" --namespace "$NAMESPACE"
    echo -e "\n${YELLOW}Deployment Status:${NC}"
    kubectl rollout status deployment/"$RELEASE_NAME" -n "$NAMESPACE" --timeout=5m || true
    echo -e "\n${YELLOW}Pod Status:${NC}"
    kubectl get pods -n "$NAMESPACE" -l app=cat-api
}

cmd_logs_app() {
    parse_args "$@"
    echo -e "${YELLOW}Cat API Application Logs:${NC}"
    kubectl logs -f deployment/"$RELEASE_NAME" -n "$NAMESPACE" --all-containers=true
}

cmd_logs_db() {
    parse_args "$@"
    echo -e "${YELLOW}PostgreSQL Database Logs:${NC}"
    kubectl logs -f statefulset/"$RELEASE_NAME"-postgres -n "$NAMESPACE" || true
}

main() {
    if [ $# -eq 0 ]; then
        print_usage
        exit 1
    fi

    check_dependencies
    
    COMMAND=$1
    shift
    
    case "$COMMAND" in
        install)
            cmd_install "$@"
            ;;
        upgrade)
            cmd_upgrade "$@"
            ;;
        uninstall)
            cmd_uninstall "$@"
            ;;
        dry-run)
            cmd_dry_run "$@"
            ;;
        lint)
            cmd_lint "$@"
            ;;
        values)
            cmd_values "$@"
            ;;
        status)
            cmd_status "$@"
            ;;
        logs-app)
            cmd_logs_app "$@"
            ;;
        logs-db)
            cmd_logs_db "$@"
            ;;
        help)
            print_usage
            ;;
        *)
            echo -e "${RED}Unknown command: $COMMAND${NC}"
            print_usage
            exit 1
            ;;
    esac
}

main "$@"
