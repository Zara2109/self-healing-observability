\# Self-Healing Infrastructure \& Complete Observability Platform



A hands-on DevOps project demonstrating application monitoring, centralized logging, distributed tracing, alert-driven incident response, and automated application recovery using Docker and Ansible.



\## Project Overview



This project simulates an application outage and uses a monitoring and recovery pipeline to detect the failure, trigger an alert, restart the application through Ansible, and verify application health.



The entire environment runs locally using Docker Compose, avoiding the need for paid cloud infrastructure.



\## Architecture



```text

&#x20;                 User Request

&#x20;                      |

&#x20;                   NGINX

&#x20;                      |

&#x20;                Node.js App

&#x20;                      |

&#x20;          +-----------+-----------+

&#x20;          |           |           |

&#x20;      Prometheus    Logs       Traces

&#x20;          |           |           |

&#x20;     Alert Rules   Loki/Alloy    Jaeger

&#x20;          |

&#x20;     Alertmanager

&#x20;          |

&#x20;     Flask Webhook

&#x20;          |

&#x20;      Recovery API

&#x20;          |

&#x20;        Ansible

&#x20;          |

&#x20;   Restart Application

&#x20;          |

&#x20;    Health Verification

```



\## Technology Stack



\- \*\*Application:\*\* Node.js, Express

\- \*\*Reverse Proxy:\*\* NGINX

\- \*\*Containers:\*\* Docker, Docker Compose

\- \*\*Metrics and Alerting:\*\* Prometheus, Alertmanager

\- \*\*Dashboards:\*\* Grafana

\- \*\*Centralized Logging:\*\* Loki, Grafana Alloy

\- \*\*Distributed Tracing:\*\* OpenTelemetry, Jaeger

\- \*\*Automation:\*\* Ansible

\- \*\*Webhook and Recovery API:\*\* Python, Flask

\- \*\*Development Environment:\*\* Windows, PowerShell, VS Code, Docker Desktop



\## Key Features



\### 1. Application Monitoring



\- Exposes application metrics through a Prometheus-compatible endpoint.

\- Tracks HTTP request counts and request duration.

\- Uses Prometheus scrape targets to monitor application availability.



\### 2. Alerting



Two Prometheus alert rules are configured:



\- \*\*ApplicationDown:\*\* Detects when Prometheus cannot scrape the Node.js application.

\- \*\*HighErrorRate:\*\* Detects an elevated proportion of HTTP 5xx responses when sufficient traffic is present.



Alertmanager forwards notifications to a local Flask webhook.



\### 3. Automated Recovery



The recovery workflow uses a dedicated Flask API and Ansible playbook.



When the webhook receives a firing `ApplicationDown` alert, it sends an authenticated request to the recovery API. The API validates the recovery token and approved alert name, applies a cooldown, and runs the Ansible playbook.



The playbook verifies that the target container exists, restarts it, and checks the application's health endpoint.



\### 4. Observability



\- \*\*Grafana:\*\* Metrics visualization and dashboards

\- \*\*Loki and Alloy:\*\* Centralized container logs

\- \*\*Jaeger and OpenTelemetry:\*\* Distributed tracing



These components help investigate application behavior and troubleshoot failures.



\## Recovery Test Results



A controlled failure test was performed by stopping the Node.js application container.



The observed results were:



1\. Prometheus detected the application outage.

2\. The `ApplicationDown` alert reached the Flask webhook.

3\. The webhook requested recovery and received HTTP 200 with `recovery\_completed`.

4\. The recovery logs showed that Ansible restarted the application container.

5\. The Ansible health check succeeded after one retry, with `failed=0`.

6\. The webhook subsequently received the resolved alert.

7\. The application health endpoint returned `healthy`, and the Compose services were running.



\*\*Result:\*\* The alert-to-Ansible recovery workflow was successfully demonstrated.



Note: Docker's own `restart: unless-stopped` policy is also enabled. Further testing can isolate Ansible-driven recovery from Docker's automatic restart behavior.



\## Local Setup



\### Prerequisites



\- Docker Desktop

\- Docker Compose

\- Git

\- PowerShell or a terminal

\- VS Code (recommended)



\### Start the project



Clone the repository, navigate to the project directory, and start the services:



```powershell

docker compose up -d --build

```



Inspect service status:



```powershell

docker compose ps

```



Validate the Compose configuration:



```powershell

docker compose config --quiet

```



\### Access the local services



| Service | Local URL |

|---|---|

| Application through NGINX | http://localhost:8080 |

| Application health check | http://localhost:8080/health |

| Prometheus | http://localhost:9090 |

| Grafana | http://localhost:3001 |

| Alertmanager | http://localhost:9093 |

| Jaeger UI | http://localhost:16686 |

| Loki API | http://localhost:3100 |



The webhook and recovery API are intended for internal Docker-network communication, with the webhook also published locally on port 5001.



\### View logs



```powershell

docker compose logs --tail=50

```



View a specific service:



```powershell

docker compose logs --tail=50 webhook

docker compose logs --tail=50 recovery

```



\### Verify application health



```powershell

Invoke-RestMethod http://localhost:8080/health

```



Expected response:



```json

{

&#x20; "status": "healthy"

}

```



\## Security Considerations



\- Keep `recovery/.env` out of version control.

\- Never commit recovery tokens, passwords, or other secrets.

\- Keep the recovery API internal to the Docker network.

\- Docker socket access grants substantial control over the Docker environment; use it only in a trusted local lab or an appropriately secured environment.

\- The recovery API restricts automated actions to the approved `ApplicationDown` alert and uses token validation and a cooldown.

\- Use a production WSGI server and additional access controls before adapting the Flask services for production.



\## Skills Demonstrated



\- Containerization and multi-service orchestration

\- Prometheus monitoring and alert-rule configuration

\- Alertmanager webhook integration

\- Python API development

\- Ansible automation and health verification

\- Centralized logging and distributed tracing

\- Incident simulation and troubleshooting

\- Secure handling of configuration secrets

\- End-to-end testing of automated recovery



\## Future Improvements



\- Build a dedicated Grafana dashboard with service-level metrics.

\- Add recovery metrics and a recovery history.

\- Test failure scenarios independently of Docker's restart policy.

\- Add automated configuration and integration tests.

\- Improve webhook authentication, retry handling, and recovery audit logging.

\- Add CI validation for Docker Compose and Ansible configuration.



\---



\*\*Project type:\*\* Hands-on DevOps and observability lab  

\*\*Environment:\*\* Local Docker Compose  

\*\*Focus:\*\* Monitoring, alerting, automated recovery, and troubleshooting



