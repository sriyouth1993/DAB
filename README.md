# DAB
This repository is dedicated to managing all Databricks Asset Bundle deployments. It includes Databricks notebooks and data jobs. The repo also covers workflows, AIML, and LDP components. Cluster configurations for job clusters are maintained here. Cluster policies required for deployments are also included.

**#What is a Databricks Asset Bundle?**
A Databricks Asset Bundle is a declarative and structured way to define, manage, and deploy Databricks resources as code. It allows teams to package Databricks assets such as notebooks, jobs, workflows, clusters, permissions, and configurations into a single, version-controlled bundle that can be deployed consistently across environments.
Databricks Asset Bundles follow an infrastructure-as-code approach, enabling automated, repeatable, and auditable deployments instead of manual configuration through the Databricks UI.

**#Backend and Frontend Architecture of Asset Bundles**
Databricks Asset Bundles use a two-layer architecture:
**Frontend**: YAML configuration files
**Backend**: Terraform-based execution engine
From the user’s perspective, all configurations are written in YAML files, which define workflows, notebooks, clusters, variables, permissions, and environment settings. These YAML files act as the frontend interface for developers and DevOps teams.
In the backend, Databricks internally translates these YAML definitions into Terraform resources. Terraform is used as the execution engine to compute the desired state, compare it with the existing state of the Databricks workspace, and apply the necessary changes. This abstraction allows users to benefit from Terraform’s reliability and state management without writing or maintaining Terraform code directly.

**.github/workflows**
The .github/workflows directory is dedicated to managing all CI/CD workflows for this repository. The workflow described here is responsible for validating and deploying Databricks Asset Bundles across Development, User Acceptance Testing, and Production environments.

This pipeline supports deployments to two Azure regions and uses a parallel deployment strategy through a matrix-based regional configuration. As a result, bundle validation and deployment are executed simultaneously for each configured region, ensuring consistency across geographically distributed Databricks workspaces.

Authentication to the Databricks workspaces is performed using an Azure Active Directory service principal with OpenID Connect (OIDC). Federated credentials are configured in the Azure App Registration for this specific GitHub repository, allowing GitHub Actions to authenticate securely without using client secrets or Databricks access tokens.

During the validation phase, the pipeline validates the Databricks Asset Bundle configuration. This includes verifying all Databricks notebooks for syntax correctness, validating data workflows, checking cluster configurations, notification settings, variable definitions, and other bundle-related configurations. If any misconfiguration or syntax error is detected during this stage, the pipeline fails immediately and prevents deployment to the target workspace.

The pipeline follows a controlled branching strategy. From any feature branch, developers can validate and deploy changes only to the Development workspace for early testing. Deployments to the User Acceptance Testing and Production environments are restricted to the main branch, ensuring that only reviewed and approved code is promoted to higher environments. These branch-based conditions are explicitly enforced within the workflow configuration.

At present, the pipeline does not include additional control gates such as static code analysis or security scanning tools like SonarQube. However, such integrations can be added as an intermediate step before the bundle validation stage to enhance code quality and security compliance.

Overall, this workflow enables teams to validate and deploy Databricks Asset Bundles reliably from the main branch while maintaining environment isolation, secure authentication, parallel regional deployments, and clear promotion controls across Development, UAT, and Production environments.
