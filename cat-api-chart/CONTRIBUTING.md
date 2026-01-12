# Contributing to Cat API Helm Chart

This document provides guidelines for contributing to the Cat API Helm chart.

## Chart Structure

```
cat-api-chart/
├── Chart.yaml                 # Chart metadata and dependencies
├── values.yaml               # Default configuration values
├── .helmignore              # Files to ignore when packaging
├── README.md                # Chart documentation
├── CONTRIBUTING.md          # This file
├── deploy.sh                # Deployment script
├── templates/               # Main chart templates
│   ├── _helpers.tpl        # Template helpers
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── serviceaccount.yaml
│   ├── service.yaml
│   ├── deployment.yaml
│   ├── ingress.yaml
│   ├── migration-job.yaml
│   └── NOTES.txt
├── charts/                  # Subchart dependencies
│   └── postgres/           # PostgreSQL subchart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── examples/               # Example configuration values
│   ├── values-development.yaml
│   ├── values-production.yaml
│   └── values-external-db.yaml
```

## Development Workflow

### Prerequisites

- Helm 3.0+
- Kubernetes 1.19+ (local cluster like minikube or kind)
- kubectl
- Docker (for building images)

### Local Testing

1. **Lint the chart:**
   ```bash
   helm lint ./cat-api-chart --strict
   ```

2. **Validate template rendering:**
   ```bash
   helm template ./cat-api-chart
   ```

3. **Dry-run installation:**
   ```bash
   helm install cat-api-test ./cat-api-chart --dry-run=client
   ```
   or using the deploy script:
   ```bash
   cd cat-api-chart
   ./deploy.sh dry-run
   ```

4. **Install to local cluster:**
   ```bash
   helm install cat-api-test ./cat-api-chart -n cat-api-test --create-namespace
   ```

5. **Test the deployment:**
   ```bash
   kubectl port-forward -n cat-api-test svc/cat-api-test 8000:8000
   curl http://localhost:8000
   ```

6. **View logs:**
   ```bash
   kubectl logs -f deployment/cat-api-test -n cat-api-test
   kubectl logs -f statefulset/cat-api-test-postgres -n cat-api-test
   ```

7. **Uninstall:**
   ```bash
   helm uninstall cat-api-test -n cat-api-test
   ```

## Making Changes

### Adding New Templates

1. Create a new YAML file in `templates/` directory
2. Use consistent naming: `<resource-kind>.yaml` (e.g., `hpa.yaml`)
3. Follow the template conventions used in existing templates
4. Include appropriate labels and selectors using `_helpers.tpl`
5. Add configuration options to `values.yaml`
6. Test with `helm template` before installing

### Modifying Values

1. Edit `values.yaml` with new configuration options
2. Include comments explaining each option
3. Organize related values under logical sections
4. Provide sensible defaults
5. Document any required values
6. Update example values files if needed

### Best Practices

#### Labels and Annotations
Use consistent labels and annotations:
```yaml
labels:
  {{- include "cat-api.labels" . | nindent 4 }}

annotations:
  checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

#### Conditional Features
Use `enabled` flags for optional features:
```yaml
{{- if .Values.catApi.enabled }}
# resource definition
{{- end }}
```

#### Resource Limits
Always define resource requests and limits:
```yaml
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

#### Security
Follow security best practices:
```yaml
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: false
  capabilities:
    drop:
      - ALL
```

#### Naming
Use consistent naming patterns:
- Templates use full release names: `{{ .Release.Name }}-component`
- ConfigMaps: `{{ include "cat-api.fullname" . }}-config`
- Secrets: `{{ include "cat-api.fullname" . }}-secret`

## Testing Checklist

Before submitting changes:

- [ ] Run `helm lint ./cat-api-chart --strict`
- [ ] Run `helm template ./cat-api-chart` without errors
- [ ] Test with `helm install --dry-run=client`
- [ ] Install to local cluster and verify all pods are running
- [ ] Check logs for errors: `kubectl logs -f deployment/<name> -n <namespace>`
- [ ] Verify database migrations run successfully
- [ ] Test with different values files (production, development, external-db)
- [ ] Verify all Kubernetes resources are created correctly:
  - `kubectl get configmaps`
  - `kubectl get secrets`
  - `kubectl get services`
  - `kubectl get ingress`
- [ ] Test upgrade scenario: `helm upgrade`
- [ ] Test uninstall: `helm uninstall`

## Testing with Different Configurations

### Development Configuration
```bash
helm install cat-api-dev ./cat-api-chart \
  -f examples/values-development.yaml \
  -n cat-api-dev --create-namespace
```

### Production Configuration
```bash
helm install cat-api-prod ./cat-api-chart \
  -f examples/values-production.yaml \
  -n cat-api-prod --create-namespace
```

### External Database Configuration
```bash
helm install cat-api-ext ./cat-api-chart \
  -f examples/values-external-db.yaml \
  -n cat-api-ext --create-namespace
```

## Updating Dependencies

When updating subchart dependencies:

```bash
# Update Chart.yaml dependency version
# Then run:
helm dependency update ./cat-api-chart

# This creates/updates Chart.lock and charts/ directory
```

## Documentation

When making changes, update relevant documentation:

- **README.md** - Main documentation and usage
- **NOTES.txt** - Post-install instructions
- Values comments - Explain new configuration options
- **examples/** - Add/update example configurations
- **CONTRIBUTING.md** - This file if workflows change

## Code Style

### YAML Formatting
- Use 2 spaces for indentation
- Consistent quote usage (prefer single quotes for simple strings)
- Use proper escaping for special characters

### Helm Template Best Practices
- Use `{{- if }}` and `{{- end }}` for whitespace control
- Include proper nindent values for nested content
- Always include context (`.`) when calling helper functions
- Use meaningful variable names
- Add comments for complex logic

### Example:
```yaml
{{- if .Values.feature.enabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "chart.fullname" . }}-config
  {{- with .Values.feature.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
data:
  key: {{ .Values.feature.value | quote }}
{{- end }}
```

## Git Workflow

1. Create a branch for your changes: `git checkout -b feature/my-feature`
2. Make your changes
3. Test thoroughly
4. Commit with clear messages
5. Push to your branch
6. Create a pull request with a clear description

## Common Issues and Solutions

### Issue: "duplicate key: ..."
**Solution**: Check for duplicate keys in YAML files. YAML keys must be unique.

### Issue: "connection refused" after installation
**Solution**: Check pod status and logs:
```bash
kubectl get pods
kubectl logs <pod-name>
```
Ensure database is ready before application starts.

### Issue: Migration job fails
**Solution**: 
- Check migration job logs: `kubectl logs job/cat-api-migration`
- Verify database connectivity
- Check database credentials in secrets

### Issue: Image pull errors
**Solution**: 
- Verify image exists: `docker pull <image>`
- Update `imagePullPolicy` in values.yaml
- For private registries, create ImagePullSecret

## Release Process

1. Update Chart.yaml version
2. Update appVersion if application changed
3. Run full test suite
4. Package the chart: `helm package ./cat-api-chart`
5. Create release notes
6. Tag the release: `git tag v1.x.x`

## Support

For questions or issues:
1. Check existing documentation
2. Review chart logs: `kubectl logs`
3. Check values configuration
4. Consult Helm best practices: https://helm.sh/docs/chart_best_practices/

## References

- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/best-practices/)
- [Chart Best Practices](https://helm.sh/docs/chart_best_practices/)
