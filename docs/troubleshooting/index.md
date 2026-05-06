# Troubleshooting

Common issues and solutions for DClaw Secure.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-secure

# Check logs
kubectl logs -n dclaw-secure deployment/dclaw-secure-backend

# Check database
kubectl get clusters -n dclaw-secure
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
