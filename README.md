# School Dashboard Jenkins + Kubernetes + ArgoCD Pipeline

## Flow

1. Developer pushes code to GitHub
2. Jenkins webhook triggers pipeline
3. Jenkins checks out latest code
4. OWASP Dependency Check runs
5. SonarQube scans code quality
6. Docker builds frontend and backend images
7. Trivy scans Docker images
8. Jenkins pushes images to Docker Hub
9. Jenkins updates image tags inside Kubernetes manifests
10. Jenkins pushes manifest changes to GitHub
11. ArgoCD detects Git change
12. ArgoCD deploys app to Kubernetes
13. Prometheus scrapes metrics
14. Grafana shows dashboards

## Required Jenkins credentials

- dockerhub-creds
- github-creds

## Required tools on Jenkins

- Docker
- Trivy
- Sonar Scanner
- OWASP Dependency Check
- Git
- JDK 17
- Node 18

## Required updates
