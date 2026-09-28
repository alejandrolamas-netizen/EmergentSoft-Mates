# EmergentSoft Ecosystem Resource Matrix

This catalog defines optional technical integration targets for ACA and the broader EmergentSoft stack. Listing a resource does not claim a commercial partnership, endorsement, certification or reseller authorization.

## NVIDIA

| Resource | Integration target | Enterprise use |
|---|---|---|
| NVIDIA NIM | Model inference endpoint | Governed AI inference |
| NVIDIA Triton Inference Server | Model serving | High-throughput inference |
| NVIDIA NeMo | Model customization/evaluation | Model adaptation and evaluation |
| NVIDIA CUDA | Accelerated compute | GPU-accelerated workloads |
| NVIDIA TensorRT | Inference optimization | Latency and cost optimization |
| NVIDIA AI Enterprise | Enterprise AI software | Production AI environments |
| NVIDIA DGX Cloud | AI infrastructure | Training and accelerated workloads |
| NVIDIA AI Blueprints | Reference AI workflows | Repeatable enterprise patterns |
| NVIDIA NGC | Containers/models/software | Artifact distribution and deployment |

Recommended NVIDIA metadata: GPU/model family, endpoint, model/version, environment, tenant ID, data classification, security policy, approval state, evaluation status and audit event ID.

## Microsoft

| Resource | Integration target | Enterprise use |
|---|---|---|
| Microsoft Foundry / Azure AI | AI application and agent layer | Enterprise AI orchestration |
| Azure OpenAI | Foundation-model access | Controlled model inference |
| Microsoft Fabric | Data/analytics | Evidence and operational analytics |
| Microsoft Entra ID | Identity | SSO and workforce identity |
| Microsoft Defender for Cloud | Security posture | Findings and remediation |
| Microsoft Purview | Data governance | Classification and compliance |
| Power Platform | Workflow/automation | Remediation and approvals |
| Microsoft Teams | Collaboration | Tasks, alerts and approvals |
| Dynamics 365 | CRM/business operations | Customer context |
| GitHub | SDLC/security | Code, CI/CD and security workflows |

Recommended Microsoft metadata: Entra tenant ID, application/client ID, environment, data classification, control framework, evidence source, finding ID, remediation status, approval state and audit event ID.

## AWS foundation

AWS Marketplace SaaS Contract; Marketplace Metering/Entitlement APIs; ECS/Fargate; ECR; RDS PostgreSQL; VPC; ALB; WAF; Secrets Manager; CloudWatch; CloudTrail; EventBridge; IAM; Certificate Manager; Well-Architected Framework.

## Cross-vendor positioning

EmergentSoft control/orchestration plane → AWS infrastructure and Marketplace → NVIDIA accelerated compute/AI software → Microsoft identity, data, security and business systems.

Vendor resources should remain configurable adapters rather than hard dependencies wherever practical. This keeps ACA deployable in AWS-native, NVIDIA-heavy, Microsoft-heavy or mixed enterprise environments.
