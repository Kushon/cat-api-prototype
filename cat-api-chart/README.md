# Cat API Helm Chart

A production-ready Helm chart for deploying the Cat API FastAPI application with PostgreSQL database.

## Overview

This Helm chart packages the Cat API application with all its dependencies, following Kubernetes and Helm best practices:

- **Modular Design**: PostgreSQL is included as a subchart dependency
- **Configuration Management**: All settings are externalized in `values.yaml`
- **Security**: Database credentials managed via Kubernetes Secrets
- **Database Migrations**: Automatic migrations on deployment via Helm hooks
- **High Availability Ready**: Support for replicas, HPA, and resource limits

## Chart Structure

```
cat-api-chart/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── README.md              # This file
├── templates/
│   ├── _helpers.tpl       # Template helpers and functions
│   ├── namespace.yaml     # Kubernetes Namespace
│   ├── configmap.yaml     # ConfigMaps for app configuration
│   ├── secret.yaml        # Kubernetes Secrets
│   ├── serviceaccount.yaml # Service Account for RBAC
│   ├── service.yaml       # Kubernetes Service
│   ├── deployment.yaml    # Main application Deployment
│   ├── ingress.yaml       # Ingress for external access
│   ├── migration-job.yaml # Database migration Job
│   └── NOTES.txt          # Post-install notes
└── charts/
    └── postgres/          # PostgreSQL subchart
        ├── Chart.yaml
        ├── values.yaml
        ├── templates/
        │   ├── _helpers.tpl
        │   ├── configmap.yaml
        │   ├── secret.yaml
        │   ├── service.yaml
        │   └── statefulset.yaml
```

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Docker image for cat-api available in your registry

## Quick Start

### Install the chart

```bash
# Using default values
helm install cat-api-release ./cat-api-chart --namespace cat-api-ns --create-namespace

# Using custom values file
helm install cat-api-release ./cat-api-chart -f custom-values.yaml --namespace cat-api-ns

# Setting specific values
helm install cat-api-release ./cat-api-chart \
  --set catApi.image.tag=v1.0.0 \
  --set postgres.auth.password=securepassword \
  --namespace cat-api-ns
```

### Upgrade the chart

```bash
helm upgrade cat-api-release ./cat-api-chart --namespace cat-api-ns
```

### Uninstall the chart

```bash
helm uninstall cat-api-release --namespace cat-api-ns
```

### Dry run test

```bash
helm install cat-api-release ./cat-api-chart --dry-run --debug
```

## Configuration

### Common Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.namespace` | Kubernetes namespace | `cat-api-ns` |
| `global.environment` | Environment type | `development` |
| `catApi.image.repository` | Cat API image repository | `cat-api` |
| `catApi.image.tag` | Cat API image tag | `latest` |
| `catApi.deployment.replicas` | Number of replicas | `1` |
| `catApi.service.port` | Service port | `8000` |

### PostgreSQL Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgres.enabled` | Enable PostgreSQL subchart | `true` |
| `postgres.image.repository` | PostgreSQL image | `postgres` |
| `postgres.image.tag` | PostgreSQL version | `15` |
| `postgres.auth.username` | Database username | `postgres` |
| `postgres.auth.password` | Database password | `postgres` |
| `postgres.storage.size` | Storage size | `5Gi` |

### Cat API Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `catApi.enabled` | Enable Cat API deployment | `true` |
| `catApi.config.DB_HOST` | Database host | (set by postgres subchart) |
| `catApi.config.DB_PORT` | Database port | `5432` |
| `catApi.config.DB_NAME` | Database name | `postgres` |
| `catApi.migration.enabled` | Enable database migrations | `true` |
| `catApi.service.type` | Service type | `ClusterIP` |
| `catApi.ingress.enabled` | Enable Ingress | `true` |

### Advanced Configuration

#### Using External PostgreSQL

To use an external PostgreSQL database instead of the subchart:

```bash
helm install cat-api-release ./cat-api-chart \
  --set postgres.enabled=false \
  --set catApi.config.DB_HOST=external-postgres.example.com \
  --set catApi.config.DB_PORT=5432 \
  --namespace cat-api-ns
```

#### Enable Autoscaling (HPA)

```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 3
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

#### Configure TLS for Ingress

```yaml
catApi:
  ingress:
    tls:
      - secretName: cat-api-tls
        hosts:
          - api.example.com
```

#### Set Resource Limits

```yaml
catApi:
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
```

## Database Migrations

Database migrations run automatically before the main deployment using Helm hooks. The migration job:

1. Executes `alembic upgrade head`
2. Uses the same image as the main application
3. Waits for PostgreSQL to be ready
4. Automatically cleans up after successful migration

To check migration status:

```bash
kubectl logs job/cat-api-release-migration -n cat-api-ns
```

## Health Checks

### Enable Application Health Checks

```yaml
catApi:
  livenessProbe:
    enabled: true
    httpGet:
      path: /health
      port: http
    initialDelaySeconds: 30
    periodSeconds: 10
  
  readinessProbe:
    enabled: true
    httpGet:
      path: /ready
      port: http
    initialDelaySeconds: 5
    periodSeconds: 5
```

### PostgreSQL Health Check

The PostgreSQL StatefulSet includes a `pg_isready` readiness probe that checks database availability.

## Security Best Practices

1. **Change default credentials**: Always change `postgres.auth.password` before deploying to production
2. **Use external secrets**: Consider using external secret management (Sealed Secrets, AWS Secrets Manager, etc.)
3. **Network policies**: Implement network policies to restrict traffic
4. **RBAC**: Service accounts and role bindings are created automatically
5. **Security contexts**: Configure pod security contexts for non-root users

### Production Security Example

```bash
helm install cat-api-release ./cat-api-chart \
  --set postgres.auth.password=<GENERATE-SECURE-PASSWORD> \
  --set catApi.secrets.postgresql.password=<GENERATE-SECURE-PASSWORD> \
  --set catApi.image.pullPolicy=IfNotPresent \
  --set catApi.podSecurityContext.runAsNonRoot=true \
  --set catApi.podSecurityContext.runAsUser=1000 \
  --namespace cat-api-ns
```

## Troubleshooting

### View Deployment Status

```bash
kubectl get deployments -n cat-api-ns
kubectl describe deployment cat-api-release -n cat-api-ns
kubectl get pods -n cat-api-ns
```

### View Pod Logs

```bash
# Application logs
kubectl logs deployment/cat-api-release -n cat-api-ns -f

# PostgreSQL logs
kubectl logs statefulset/cat-api-release-postgres -n cat-api-ns
```

### Check ConfigMaps and Secrets

```bash
kubectl get configmaps -n cat-api-ns
kubectl get secrets -n cat-api-ns
```

### Verify Ingress

```bash
kubectl get ingress -n cat-api-ns
kubectl describe ingress cat-api-release -n cat-api-ns
```

## Uninstalling

```bash
helm uninstall cat-api-release --namespace cat-api-ns
kubectl delete namespace cat-api-ns
```

## License

MIT

## Support

For issues and contributions, please visit the project repository.
