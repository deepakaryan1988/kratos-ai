# Continuous Cloud Infrastructure Security Scanning: How Major Tech Companies Do It

## Executive Summary

Major cloud providers and tech giants have evolved sophisticated approaches to continuous infrastructure security scanning, combining event-driven architectures, GitOps workflows, and policy-as-code practices. This analysis examines the frameworks, tools, and patterns used by Google, Amazon, Microsoft, Meta, and Netflix.

## 1. Open Source Projects and Tooling

### Core Security Tools

**Falco**: Acquired by Sysdig but originally created at Cornell, Falco provides runtime security monitoring through system call analysis. Google's Security Command Center integrates Falco events directly, while Netflix leveraged similar runtime monitoring before migrating to AWS-native solutions.

**Open Policy Agent (OPA)**: A CNCF graduated project adopted universally. Google's Policy Controller for GKE is built on OPA Gatekeeper. Microsoft uses OPA for Azure Policy as Code. Netflix employees have contributed to OPA ecosystem tools.

**kube-bench and kube-audit**: CIS Kubernetes Benchmark enforcement tools. Google's Pod Security Standards replace traditional PSPs. Microsoft's Defender for Containers incorporates these benchmarks.

### Company-Specific OSS Contributions

- **Google**: Policy Controller (OPA-based), Binary Authorization
- **Amazon**: cfn-nag (CloudFormation Linter), guard-duty tools
- **Microsoft**: EPAC (Enterprise Policy as Code) PowerShell module
- **Meta**: Zoncolan (Hack static analyzer), Pysa (Python security analyzer), Mariana Trench (Android security analyzer)
- **Netflix**: Security Monkey (now in maintenance mode), Simian Army

## 2. Framework Patterns: Event-Driven vs Polling vs GitOps

### Hybrid Architecture Dominance

Modern implementations combine all three patterns:

**Event-Driven (Real-time)**:
- AWS Lambda-triggered Config rules on resource changes
- Google Security Command Center real-time mode for configuration changes
- Falco system call monitoring with immediate alerting

**Polling (Scheduled)**:
- Google Security Health Analytics daily batch scans
- kube-bench recurring CIS benchmark runs
- Netflix's Security Monkey periodic account sweeps

**GitOps (Declarative)**:
- Azure Policy as Code with GitHub integration
- OPA Gatekeeper policy stored in Git repositories
- Conftest for pre-commit IaC validation

### Implementation Pattern

```
┌─────────────┐    ┌──────────┐    ┌───────────────┐
│   Event     │    │  GitOps  │    │   Polling     │
│(Real-time)  │    │(Declare) │    │ (Scheduled)   │
└──────┬──────┘    └────┬─────┘    └──────┬────────┘
       │               │                 │
       └───────────────┼─────────────────┘
                       │
          ┌────────────▼────────────┐
          │  Policy Enforcement     │
          │  (OPA/Gatekeeper,       │
          │   Azure Policy,         │
          │   Security Command Ctr) │
          └────────────────────────┘
```

## 3. False Positive Handling and Alert Fatigue

### Multi-Layered Filtering

Companies employ sophisticated filtering approaches:

**Namespace Exclusions**: OPA Gatekeeper uses `excludedNamespaces` to skip system namespaces from policy evaluation, reducing noise from kube-system resources.

**Scoped Enforcement**: Gatekeeper's `enforcementAction: scoped` allows opt-out of audit for specific constraints, enabling gradual rollout and targeted monitoring.

**Violation Limit Configuration**: Both OPA Guardrails and AWS Config allow configuring violation limits per constraint, preventing overwhelming result sets.

**Gradual Rollout Pattern**:
1. Start policies in `dryrun` or `audit` mode
2. Review violations to identify common false positives
3. Add exceptions for legitimate use cases
4. Move to `warn` mode with notifications
5. Finally enforce with `deny` action

### Alert Consolidation

Google's Security Command Center aggregates findings from multiple sources (Falco, custom modules) into unified alerts. Microsoft's Defender for Cloud similarly combines security posture findings from multiple services into single security alerts with severity scoring.

## 4. Infrastructure-as-Code Integration

### Terraform and CloudFormation Scanning

**Pre-Commit Validation**:
- Conftest validates Terraform plans before deployment using OPA policies
- tfsec and checkov integrate into CI pipelines for static analysis
- AWS cfn-nag scans CloudFormation templates for security issues

**Shift-Left Security**:
- Google's IaC validation in Security Command Center checks Terraform plans against organization policies
- Microsoft Defender for DevOps scans repositories and pipelines for security misconfigurations
- Netflix's implementation validates security before resources hit production

### Policy-as-Code Implementation

Azure's recommended pattern stores policy definitions in Git repositories with:
- Pull request workflow for policy changes
- Automated testing of policy definitions
- Promotion from Dev → Test → Prod environments

```yaml
# Example OPA ConstraintTemplate for Kubernetes
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items: string
```

## 5. Self-Healing and Auto-Remediation

### Reactive Remediation Patterns

**AWS Systems Manager Automation**:
- AWS Config rules trigger Systems Manager documents for automatic remediation
- Example: Non-compliant S3 bucket triggers automation to enable encryption
- Closed-loop remediation with verification

**Kubernetes Admission Control**:
- OPA Gatekeeper blocks non-compliant resources at creation time
- Kyverno can mutate resources to add required configurations
- Policy enforced continuously rather than after-the-fact fixes

### Proactive Remediation

Microsoft's approach uses Defender for Cloud's regulatory compliance dashboard to:
1. Identify non-compliant resources
2. Provide remediation steps in the Azure portal
3. Enable one-click remediation for common issues

Google's Security Command Center provides:
- Custom Security Health Analytics modules for organization-specific remediation
- Integration with Cloud Functions for automated response workflows

### GitOps Remediation Loop

Modern GitOps security integrates remediation as code:
```
1. Policy violation detected (Gatekeeper/Kyverno)
2. Violation recorded in Git as desired state
3. GitOps controller applies corrective configuration
4. Policy re-evaluation confirms compliance
```

## Conclusion

Major tech companies converge on hybrid approaches combining event-driven real-time monitoring with GitOps declarative policies and scheduled compliance checks. Open Policy Agent has emerged as the standard policy engine, with Falco providing runtime security. False positive management through gradual rollout and scoping, integrated IaC scanning, and closed-loop remediation are key differentiators that enable these organizations to operate secure infrastructure at scale.

### Key Takeaways for Implementation

Organizations seeking to adopt these patterns should consider:

1. **Start with a hybrid approach** - implement GitOps for policy-as-code, event-driven for critical runtime detection, and scheduled scans for compliance baselines.

2. **Invest in false positive management early** - the gradual rollout pattern saves significant operational overhead.

3. **Integrate security scanning into developer workflows** through IaC validation rather than treating it as a separate security gate.

4. **Leverage managed services where possible** - AWS Security Hub, Azure Defender, and GCP Security Command Center provide integrated scanning capabilities without infrastructure overhead.

5. **Design for remediation from day one** - blocking violations is necessary but automatic correction is the goal for mature implementations.

The convergence on OPA/Gatekeeper for Kubernetes policy, Falco for runtime security, and GitOps for deployment reflects industry maturation of cloud security practices beyond point solutions toward integrated, automated security platforms.