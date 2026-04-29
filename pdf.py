from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

# ── Color palette ──────────────────────────────────────────────────────────────
MAGENTA   = colors.HexColor("#E20074")   # T-Mobile brand
DARK_GREY = colors.HexColor("#1A1A2E")
MID_GREY  = colors.HexColor("#2D2D44")
LIGHT_BG  = colors.HexColor("#F8F8FC")
ACCENT    = colors.HexColor("#FF4F9A")
WHITE     = colors.white
TEXT      = colors.HexColor("#1C1C1C")
STAR_S    = colors.HexColor("#E20074")
STAR_T    = colors.HexColor("#9B1D6B")
STAR_A    = colors.HexColor("#C0392B")
STAR_R    = colors.HexColor("#1A6D3A")
GOLD      = colors.HexColor("#F39C12")

PAGE_W, PAGE_H = letter

# ── Styles ─────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def s(name, **kw):
    return ParagraphStyle(name, **kw)

cover_title   = s("CoverTitle", fontSize=34, textColor=WHITE,
                   leading=42, alignment=TA_CENTER, fontName="Helvetica-Bold")
cover_sub     = s("CoverSub",   fontSize=15, textColor=ACCENT,
                   leading=22, alignment=TA_CENTER, fontName="Helvetica")
cover_info    = s("CoverInfo",  fontSize=11, textColor=WHITE,
                   leading=18, alignment=TA_CENTER, fontName="Helvetica")

section_hdr   = s("SectionHdr", fontSize=16, textColor=WHITE,
                   leading=22, fontName="Helvetica-Bold", backColor=MAGENTA,
                   leftIndent=-10, rightIndent=-10,
                   spaceBefore=14, spaceAfter=6,
                   borderPad=6)

q_title       = s("QTitle", fontSize=12, textColor=MAGENTA,
                   leading=16, fontName="Helvetica-Bold",
                   spaceBefore=12, spaceAfter=3)

star_s        = s("StarS", fontSize=10, textColor=STAR_S,
                   leading=15, fontName="Helvetica-Bold",
                   leftIndent=12, spaceBefore=5)
star_t        = s("StarT", fontSize=10, textColor=STAR_T,
                   leading=15, fontName="Helvetica-Bold",
                   leftIndent=12)
star_a        = s("StarA", fontSize=10, textColor=STAR_A,
                   leading=15, fontName="Helvetica-Bold",
                   leftIndent=12)
star_r        = s("StarR", fontSize=10, textColor=STAR_R,
                   leading=15, fontName="Helvetica-Bold",
                   leftIndent=12)

body          = s("Body", fontSize=10, textColor=TEXT,
                   leading=15, fontName="Helvetica",
                   leftIndent=24, spaceAfter=4, alignment=TA_JUSTIFY)

tip_style     = s("Tip", fontSize=9, textColor=colors.HexColor("#5D4037"),
                   leading=14, fontName="Helvetica-Oblique",
                   leftIndent=12, backColor=colors.HexColor("#FFF8E1"),
                   borderPad=4, spaceAfter=8)

bullet_style  = s("Bullet", fontSize=10, textColor=TEXT,
                   leading=14, fontName="Helvetica",
                   leftIndent=36, firstLineIndent=-12, spaceAfter=2)

note_style    = s("Note", fontSize=9, textColor=colors.HexColor("#1565C0"),
                   leading=13, fontName="Helvetica-Oblique", leftIndent=12)

toc_item      = s("TOCItem", fontSize=11, textColor=DARK_GREY,
                   leading=18, fontName="Helvetica", leftIndent=20)

# ── Helper builders ────────────────────────────────────────────────────────────

def hr():
    return HRFlowable(width="100%", thickness=1, color=MAGENTA, spaceAfter=6, spaceBefore=6)

def section(title, icon=""):
    tbl = Table([[Paragraph(f"{icon}  {title}", s("sh2", fontSize=14, textColor=WHITE,
                  fontName="Helvetica-Bold", leading=20))]], colWidths=[6.5*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), MAGENTA),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LEFTPADDING",  (0,0), (-1,-1), 12),
    ]))
    return tbl

def question_block(number, question, situation, task, action, result, tip=None):
    """Build one Q&A block with STAR formatting."""
    elems = []
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(f"Q{number}. {question}", q_title))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD"), spaceAfter=4))

    elems.append(Paragraph("★  SITUATION", star_s))
    elems.append(Paragraph(situation, body))
    elems.append(Paragraph("▸  TASK", star_t))
    elems.append(Paragraph(task, body))
    elems.append(Paragraph("⚡  ACTION", star_a))
    elems.append(Paragraph(action, body))
    elems.append(Paragraph("✔  RESULT", star_r))
    elems.append(Paragraph(result, body))

    if tip:
        elems.append(Paragraph(f"💡 Pro Tip: {tip}", tip_style))
    return elems


def page_background(canvas, doc):
    canvas.saveState()
    # Thin left accent bar
    canvas.setFillColor(MAGENTA)
    canvas.rect(0.35*inch, 0.6*inch, 0.04*inch, PAGE_H - 1.2*inch, fill=1, stroke=0)
    # Footer
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.drawString(0.5*inch, 0.4*inch, "T-Mobile SRE Senior Engineer – L3 Interview Prep Guide   |   Confidential")
    canvas.drawRightString(PAGE_W - 0.5*inch, 0.4*inch, f"Page {doc.page}")
    canvas.restoreState()


# ── Build story ────────────────────────────────────────────────────────────────

story = []

# ── COVER PAGE ──────────────────────────────────────────────────────────────────
def cover_page(canvas, doc):
    canvas.saveState()
    # Gradient-like background
    canvas.setFillColor(DARK_GREY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Top magenta band
    canvas.setFillColor(MAGENTA)
    canvas.rect(0, PAGE_H - 2.4*inch, PAGE_W, 2.4*inch, fill=1, stroke=0)
    # Bottom accent strip
    canvas.setFillColor(MID_GREY)
    canvas.rect(0, 0, PAGE_W, 1.2*inch, fill=1, stroke=0)
    # Decorative circles
    canvas.setFillColor(colors.HexColor("#E200741A"))
    canvas.circle(6.8*inch, 1.5*inch, 1.6*inch, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#FF4F9A22"))
    canvas.circle(0.5*inch, 3*inch, 1.1*inch, fill=1, stroke=0)
    # T-Mobile logo text
    canvas.setFont("Helvetica-Bold", 28)
    canvas.setFillColor(WHITE)
    canvas.drawCentredString(PAGE_W/2, PAGE_H - 1.6*inch, "T-Mobile")
    canvas.setFont("Helvetica", 13)
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(PAGE_W/2, PAGE_H - 1.95*inch, "TMUS Global Solutions")

    canvas.setFont("Helvetica-Bold", 26)
    canvas.setFillColor(WHITE)
    canvas.drawCentredString(PAGE_W/2, PAGE_H - 3.3*inch, "SRE Senior Engineer")
    canvas.setFont("Helvetica-Bold", 20)
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(PAGE_W/2, PAGE_H - 3.75*inch, "L3 Face-to-Face Interview")
    canvas.setFont("Helvetica-Bold", 16)
    canvas.setFillColor(GOLD)
    canvas.drawCentredString(PAGE_W/2, PAGE_H - 4.15*inch, "Complete Q&A Preparation Guide")

    # Sub info
    canvas.setFont("Helvetica", 11)
    canvas.setFillColor(colors.HexColor("#CCCCCC"))
    canvas.drawCentredString(PAGE_W/2, PAGE_H - 5.0*inch, "★  STAR Method  |  Real-World Scenarios  |  Technical Deep Dives  ★")

    # What's inside table
    items = [
        ("50+", "Interview Questions with STAR Answers"),
        ("5",   "Core Topic Sections Aligned to JD"),
        ("15+", "Real-Time Production Scenario Q&As"),
        ("10",  "Behavioral & Leadership Questions"),
    ]
    y = PAGE_H - 5.9*inch
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(MAGENTA)
    canvas.drawCentredString(PAGE_W/2, y, "— What's Inside —")
    y -= 0.35*inch
    for num, desc in items:
        canvas.setFont("Helvetica-Bold", 13)
        canvas.setFillColor(ACCENT)
        canvas.drawString(1.8*inch, y, f"✦ {num}")
        canvas.setFont("Helvetica", 11)
        canvas.setFillColor(WHITE)
        canvas.drawString(2.8*inch, y, desc)
        y -= 0.28*inch

    # Bottom footer
    canvas.setFont("Helvetica-Oblique", 9)
    canvas.setFillColor(colors.HexColor("#AAAAAA"))
    canvas.drawCentredString(PAGE_W/2, 0.55*inch, "Prepared exclusively for your T-Mobile L3 Interview  •  Use Confidently  •  You've Got This! 🚀")
    canvas.restoreState()

# We'll add a blank first page for the cover
story.append(Spacer(1, 1))  # placeholder; cover drawn in onFirstPage

story.append(PageBreak())

# ── TABLE OF CONTENTS ───────────────────────────────────────────────────────────
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("📋  Table of Contents", s("toc_h", fontSize=18, textColor=MAGENTA,
              fontName="Helvetica-Bold", leading=26, spaceBefore=0, spaceAfter=10)))
story.append(hr())

toc_entries = [
    ("Section 1", "Kubernetes Architecture & Self-Healing", "3"),
    ("Section 2", "Infrastructure as Code – Terraform & Ansible", "4"),
    ("Section 3", "Cloud Platforms – AWS / Azure / Multi-Cloud", "5"),
    ("Section 4", "CI/CD, Observability & SRE Practices", "6"),
    ("Section 5", "Python / Bash Scripting & Automation", "7"),
    ("Section 6", "Real-Time Production Scenarios", "8"),
    ("Section 7", "Behavioral & Leadership Questions (L3 Focus)", "10"),
    ("Section 8", "Questions YOU Should Ask the Interviewer", "12"),
    ("Section 9", "L3 Cheat Sheet & Power Phrases", "13"),
]
for sec, title, pg in toc_entries:
    row = f"<b><font color='#E20074'>{sec}:</font></b>  {title}"
    dot_row = [[Paragraph(row, toc_item), Paragraph(f"pg {pg}", s("pgnum", fontSize=10,
                textColor=MAGENTA, fontName="Helvetica-Bold", alignment=1))]]
    t = Table(dot_row, colWidths=[5.5*inch, 1*inch])
    t.setStyle(TableStyle([
        ("LINEBELOW", (0,0), (-1,-1), 0.3, colors.HexColor("#EEEEEE")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(t)

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph(
    "💡 <b>How to Use This Guide:</b> Each answer follows the STAR method: "
    "<font color='#E20074'><b>S</b></font>ituation → "
    "<font color='#9B1D6B'><b>T</b></font>ask → "
    "<font color='#C0392B'><b>A</b></font>ction → "
    "<font color='#1A6D3A'><b>R</b></font>esult. "
    "Internalize the structure, personalize details from your own experience, and deliver with confidence.",
    tip_style))
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – KUBERNETES
# ═══════════════════════════════════════════════════════════════════════════════
story.append(section("SECTION 1: Kubernetes Architecture & Self-Healing", "☸"))
story.append(Spacer(1, 8))

story += question_block(1,
    "Walk me through a large-scale Kubernetes cluster you designed and how you ensured high availability.",
    "At my previous role, we were running 200+ microservices across a hybrid on-prem and AWS environment. The cluster had grown organically and we were seeing frequent node-level failures causing cascading outages.",
    "I was tasked with redesigning the cluster architecture to achieve 99.95% uptime SLO, reduce MTTR below 5 minutes, and ensure zero single points of failure.",
    "I architected a multi-master control plane with 3 etcd nodes using Raft consensus across separate AZs. I implemented PodDisruptionBudgets for every critical service to cap voluntary disruption. Used NodeAffinity and PodAntiAffinity rules to spread replicas across zones. Set up cluster-autoscaler for worker nodes with min/max thresholds and defined CPU/memory resource requests and limits on every pod. Configured HPA for stateless services and VPA for stateful ones. Implemented liveness and readiness probes on all pods with tuned failure thresholds.",
    "We achieved 99.97% uptime over 6 months post-redesign. Node failures were automatically remediated within 3 minutes via auto-scaling, and no manual intervention was needed during 4 separate node-level incidents. The team's on-call burden dropped by 40%.",
    "At L3, they want to hear architecture thinking, not just operations. Mention trade-offs — why 3 etcd nodes vs 5, why HPA over VPA for stateless services."
)

story += question_block(2,
    "Pods are stuck in CrashLoopBackOff — walk me through your exact debugging steps.",
    "During a peak traffic period at 2 AM, our payments microservice went into CrashLoopBackOff across 8 pods simultaneously. Alerts fired for 5xx errors and latency SLOs were breached.",
    "As the on-call SRE, I had to diagnose and restore service within our 15-minute RTO.",
    "Step 1: kubectl describe pod <pod-name> to check events — saw OOMKilled. Step 2: kubectl logs <pod-name> --previous to get the last crash logs — saw Java heap OutOfMemoryError. Step 3: Checked resource limits — memory limit was 512Mi but the app's recent feature added an in-memory cache that grew unbounded. Step 4: Immediate mitigation — kubectl set resources deployment payments --limits=memory=1Gi. Step 5: Simultaneously opened a PR to add cache eviction policy. Step 6: Monitored pod restarts — pods stabilized within 4 minutes. Step 7: Ran a post-mortem and added a memory usage alert at 80% threshold.",
    "Service restored in 6 minutes. The cache eviction PR was merged next morning. We also added Vertical Pod Autoscaler recommendations as a guardrail and updated the deployment template with resource requests matching 60% of observed p99 usage.",
    "Interviewers love systematic 'Step 1, Step 2' answers. It shows you don't panic. Mention kubectl debug, stern for multi-pod logs, and metrics-server as tools in your kit."
)

story += question_block(3,
    "A deployment rollout failed and rollback isn't working. How do you recover quickly?",
    "We had a Helm-managed deployment of our API gateway that pushed a bad config — rollback via 'helm rollback' failed because the previous release had a corrupted secret reference.",
    "Restore service within RTO of 10 minutes without data loss while also protecting other dependent services.",
    "First, I paused the rollout: kubectl rollout pause deployment/api-gateway. Then I used kubectl rollout history to identify the last good revision. Since Helm rollback failed, I used kubectl set image directly to pin the last known good container image. I patched the broken secret reference manually via kubectl edit secret. Simultaneously notified downstream teams to expect brief degradation. Once pods stabilized, I ran kubectl rollout status to confirm all replicas were healthy. Then I opened an incident in PagerDuty and started RCA.",
    "Service restored in 8 minutes. The root cause was an automated secret rotation job that ran mid-deployment without coordination. We implemented a deployment freeze window policy for secret rotations and added a pre-deploy validation script that checks secret availability before rollout begins.",
    "Show you know both kubectl-native and Helm recovery paths. Bonus: mention ArgoCD sync policies and rollback in GitOps context — very relevant for T-Mobile's stack."
)

story += question_block(4,
    "How did you design monitoring for nightly backups across hundreds of Kubernetes clusters?",
    "We managed 300+ Kubernetes clusters across multiple regions and had unreliable backup verification — we often discovered failures only when restores were needed.",
    "Design a centralized, automated backup monitoring system with alerting that could detect failures within 30 minutes of the backup window closing.",
    "I built a CronJob in each cluster that ran a backup verification script post-completion and published a success/failure metric to Prometheus Pushgateway. A central Prometheus scraped all Pushgateways. In Grafana, I built a heatmap dashboard showing backup status per cluster. Wrote AlertManager rules: if any cluster's backup metric was absent or == 0 for more than 30 minutes after the scheduled window, it fired a PagerDuty alert. Added runbook links directly in alerts. For clusters behind private networks, used a relay agent pattern.",
    "Backup success rate visibility went from 0% to 100% automated coverage. We caught 3 silent backup failures in the first week that had been happening for months. MTTR for backup issues dropped from days (discovered on restore) to under 2 hours.",
    "This shows cross-cluster observability thinking — a key L3 skill. Mention the Prometheus federation pattern or Thanos for multi-cluster metrics aggregation."
)

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – TERRAFORM & ANSIBLE
# ═══════════════════════════════════════════════════════════════════════════════
story.append(section("SECTION 2: Infrastructure as Code – Terraform & Ansible", "🏗"))
story.append(Spacer(1, 8))

story += question_block(5,
    "Describe a complex Terraform module you wrote and how deployments were triggered.",
    "Our team was manually provisioning EKS clusters for every new product team — it took 3-4 days and was error-prone with inconsistent configurations.",
    "Build a reusable, parameterized Terraform module for EKS cluster provisioning that could be consumed by any product team via a self-service workflow.",
    "I built a Terraform module with inputs for cluster size, node groups, add-ons (VPC CNI, CoreDNS, kube-proxy), and IRSA roles. Used terragrunt for DRY configuration across environments. The module provisioned VPC, subnets, IAM roles, security groups, and the EKS cluster in one apply. Deployment was triggered via GitHub Actions — PRs to the infra repo ran terraform plan; merge to main triggered terraform apply with manual approval gate for prod. State stored in S3 with DynamoDB locking. Added drift detection via a scheduled GH Actions job running terraform plan and alerting on non-empty plans.",
    "Cluster provisioning time dropped from 3-4 days to 45 minutes. 12 product teams self-onboarded in the first month. Zero configuration drift incidents in 6 months. The module was adopted as the org-wide standard.",
    "Mention remote state, workspaces, and module versioning (registry or git tags). L3 interviewers love hearing about drift detection — it's an advanced SRE practice."
)

story += question_block(6,
    "Terraform shows a critical resource will be destroyed unexpectedly. How do you handle it?",
    "During a terraform plan for a routine security group update, the output showed that our production RDS instance was scheduled for destruction — a potential data loss scenario.",
    "Prevent the destruction, understand the root cause, and safely apply only the intended changes.",
    "First, I immediately stopped the pipeline and notified the team. I reviewed the plan output carefully — the destroy was triggered because someone had manually renamed a resource in the Terraform state. I ran terraform state list to see the current state, then terraform state show on the affected resource. Used terraform state mv to rename it to match the new config — no actual cloud resource was touched. Re-ran terraform plan — the destroy was gone, only the security group change remained. Applied safely with targeted apply: terraform apply -target=aws_security_group.xyz. Added a lifecycle block with prevent_destroy = true to the RDS resource. Set up a plan review policy requiring 2-engineer sign-off for any plan containing 'destroy'.",
    "Zero data loss. The incident highlighted a process gap — we added a policy prohibiting manual state edits without peer review and implemented OPA-based plan gates that reject any plan destroying stateful resources without an explicit override.",
    "Knowing terraform state commands is pure gold at L3. Also mention: terraform import, -refresh-only, and using Sentinel or OPA for policy-as-code guardrails."
)

story += question_block(7,
    "How do you prevent Terraform state conflicts with multiple developers?",
    "Our growing team of 8 engineers was hitting frequent state lock errors and occasional state corruption as everyone worked on the same monolithic Terraform repo.",
    "Implement a workflow that allows parallel development without state conflicts while maintaining audit trails.",
    "I migrated state to S3 backend with DynamoDB locking — this provided atomic locking during apply. Split the monolithic repo into smaller stacks per domain (networking, compute, security) to reduce blast radius and contention. Implemented Atlantis for GitOps-driven Terraform — all plans/applies ran via PRs, preventing concurrent applies on the same workspace. Set up separate workspaces per environment. Enforced a policy: no local terraform apply in prod, all changes through CI. Added state backup versioning on S3.",
    "State conflicts dropped to zero. The team could work in parallel across different stacks. We had full audit trails via Atlantis PR comments. One accidental state corruption was fully recovered from S3 version history in 10 minutes.",
    "Mention Terragrunt's dependency locking and workspace isolation. For T-Mobile's scale, bring up the concept of 'stack decomposition' for reducing state size and blast radius."
)

story += question_block(8,
    "Explain your experience with Ansible for patching and configuration management at scale.",
    "We had 500+ Linux servers across RHEL and Ubuntu that needed monthly OS patches with zero unplanned downtime. Manual patching was taking a week and missing SLA windows.",
    "Automate OS patching with pre/post validation, rolling updates, and rollback capability across all servers.",
    "Built Ansible playbooks with: pre-patch tasks (disk space check, service health, snapshot trigger), rolling update strategy (serial: 20% per batch), yum/apt update with only-security filter, service restart via handlers (only triggered when packages changed), post-patch validation (service health checks, custom smoke tests). Used Ansible Vault for privileged credentials. Scheduled via Ansible Tower/AWX with approval workflows. Implemented a rollback playbook that restored from snapshot if post-patch health check failed.",
    "Patching time reduced from 1 week to 8 hours automated. Patch compliance went from 72% to 99.3%. Zero unplanned downtime incidents. The rollback playbook was triggered once and successfully restored 3 servers within 12 minutes.",
    "Handlers are a favorite interview topic. Explain: handlers only run when notified by a task, they run once at the end of the play, and they're idempotent. Show you understand the difference from regular tasks."
)

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – CLOUD PLATFORMS
# ═══════════════════════════════════════════════════════════════════════════════
story.append(section("SECTION 3: Cloud Platforms – AWS / Azure / Multi-Cloud", "☁"))
story.append(Spacer(1, 8))

story += question_block(9,
    "Design a multi-region, highly available Kubernetes setup. Walk me through your approach.",
    "A business-critical telecom application needed to serve 50 million users with 99.99% uptime SLO across US regions and tolerate full regional failure.",
    "Architect a multi-region active-active Kubernetes setup with automatic failover, data consistency, and observability across regions.",
    "Deployed EKS clusters in us-east-1 and us-west-2 with identical configurations managed via GitOps (ArgoCD). Used Route 53 with health checks and latency-based routing to distribute traffic. For stateful services, used CockroachDB (distributed SQL) with multi-region replication. Implemented Istio service mesh for cross-cluster traffic management and mTLS. Federated monitoring with Thanos for cross-cluster Prometheus metrics. Backup strategy: Velero with cross-region S3 replication. Tested failover quarterly using chaos engineering (LitmusChaos).",
    "The system withstood a simulated us-east-1 failure in a DR drill — traffic shifted to us-west-2 in under 90 seconds with no data loss. RTO: 90s, RPO: 0. SLO has been met for 18 consecutive months since deployment.",
    "This is a classic L3 architecture question. Mention the trade-offs: active-active vs active-passive, data consistency challenges (CAP theorem), cost of running dual regions, and why you chose your specific DB solution."
)

story += question_block(10,
    "Your EC2 instances are suddenly unreachable. Walk me through your troubleshooting checklist.",
    "Production EC2 instances hosting a microservice became unreachable — no SSH, no application response — affecting 30% of our API traffic.",
    "Restore connectivity ASAP while preserving forensic evidence for RCA.",
    "Checked EC2 console — instances showed 'running' but system status checks failing. Checked VPC flow logs — no inbound traffic reaching the instances. Checked security group rules — found someone had accidentally removed the inbound rule for port 443. Restored the rule immediately — connectivity restored in 2 minutes. For the SSH issue: checked NACLs — confirmed they were fine. Used EC2 Instance Connect as backup SSH path. Enabled VPC flow logs if not already active. Checked CloudWatch agent for system-level metrics. Post-incident: enabled AWS Config rules to alert on security group changes and added SCPs to prevent accidental security group deletion in prod.",
    "Connectivity restored in 4 minutes. The accidental security group change was traced to a manual console action during an unrelated task. Implemented mandatory use of IaC for all security group changes and enabled AWS Config continuous compliance monitoring.",
    "Show the systematic checklist: instance status → security group → NACL → route table → IGW → DNS. L3 interviewers love seeing you think in OSI layers."
)

story += question_block(11,
    "AWS billing suddenly spiked overnight. How do you identify and contain the cause?",
    "At 8 AM I received a Cost Anomaly Detection alert — overnight spend was 400% above baseline, adding $50K in unexpected charges.",
    "Identify the cost source, stop the bleeding, and put preventive controls in place.",
    "Opened AWS Cost Explorer with hourly granularity and filtered by service — identified EC2 as the culprit (specifically spot instance fleet). Checked the Auto Scaling group — found max capacity had been changed from 10 to 1000 in a test config that got promoted to prod. Immediately set ASG max back to 10 and terminated excess instances via CLI. Checked for any active EMR clusters or RDS snapshots — found an engineer had triggered a full-history data export that spawned 200 instances. Communicated status to finance and leadership. Set up budget alerts at 80% and 100% of monthly budget with SNS notifications.",
    "Instances terminated within 20 minutes of investigation start. Excess spend was $38K — partially offset by spot pricing. We implemented: AWS Service Control Policies capping max instance count, mandatory cost tagging enforcement, and a pre-prod checklist that includes cost estimation sign-off for any ASG config change.",
    "Knowing Cost Explorer filters, Cost Anomaly Detection, and Trusted Advisor are L3-level skills. Mention FinOps — it aligns perfectly with T-Mobile's cost optimization expectations."
)

story += question_block(12,
    "A misconfigured S3 bucket exposed public data. What is your immediate mitigation plan?",
    "Security team notified us at 3 AM that an S3 bucket containing customer configuration files had a public ACL — potentially exposed for 4 hours based on CloudTrail logs.",
    "Immediately contain the exposure, assess impact, notify stakeholders, and prevent recurrence.",
    "Step 1 (T+0): Immediately ran 'aws s3api put-public-access-block' to block all public access. Step 2 (T+2min): Preserved CloudTrail logs and S3 server access logs to a separate secured bucket for forensics. Step 3 (T+5min): Identified what data was in the bucket — config files with no PII or credentials confirmed. Step 4 (T+10min): Notified CISO, legal, and on-call SRE lead. Step 5: Checked other buckets for similar misconfiguration using AWS Config rule 's3-bucket-public-read-prohibited'. Step 6: Filed an incident ticket with a 24-hour RCA deadline.",
    "Exposure contained in under 3 minutes. Forensic analysis confirmed no sensitive data was accessed (CloudFront logs showed no external hits during the window). Post-incident: enabled AWS S3 Block Public Access at the account level, implemented AWS Config continuous compliance with auto-remediation Lambda, and added pre-commit hooks to Terraform that reject any S3 bucket config with public ACLs.",
    "Security questions are guaranteed at L3. Show you know the response order: contain → preserve evidence → assess → notify → remediate. Never reverse the first two."
)

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – CI/CD, OBSERVABILITY & SRE PRACTICES
# ═══════════════════════════════════════════════════════════════════════════════
story.append(section("SECTION 4: CI/CD, Observability & SRE Practices", "📊"))
story.append(Spacer(1, 8))

story += question_block(13,
    "Describe a major production incident you handled end-to-end. What were the lessons?",
    "We experienced a complete outage of our payment processing service affecting 2 million users during a Black Friday peak window. Revenue impact was $1.2M/hour.",
    "As incident commander, restore service within 30 minutes, communicate transparently, and prevent recurrence.",
    "Declared SEV-1 immediately and set up a war room bridge. Identified from Grafana that DB connection pool was exhausted — caused by a recent deploy that removed connection pooling config. Rolled back the deployment in 8 minutes via ArgoCD. Connections recovered, but DB was still lagging — ran a manual VACUUM on PostgreSQL to clear dead tuples. Service restored at T+22 minutes. Communicated status updates every 5 minutes on the status page. Ran a full post-mortem within 48 hours: 5 Whys analysis, blameless culture, published findings to entire engineering org.",
    "Service restored in 22 minutes — within SLO RTO. Post-mortem produced 7 action items: connection pool config added to deploy checklist, a canary deployment policy for DB-touching changes, automated regression tests for connection pool settings, and DB health dashboards. The incident actually improved our overall incident response process.",
    "L3 interviewers want to see incident commander mindset: delegation, communication cadence, blameless culture, and systematic RCA. Use the '5 Whys' framing explicitly."
)

story += question_block(14,
    "How do you build and manage error budgets? What happens when you exhaust them?",
    "Our platform had a 99.9% availability SLO but we had no formal error budget tracking — every reliability vs velocity decision was a political battle.",
    "Implement a formal error budget policy that gives the team objective data to balance feature delivery with reliability work.",
    "Calculated error budget: 99.9% SLO = 43.8 minutes of allowed downtime per month. Built Prometheus recording rules to calculate error rate per service. Created Grafana dashboards showing: error budget remaining (%), burn rate (fast vs slow burn), and projected depletion date. Defined policy: >50% budget consumed → reliability work prioritized; >80% → feature freeze; 100% → mandatory reliability sprint. Set up burn rate alerts: 2% burn in 1 hour triggered page; 5% in 6 hours triggered SEV-2.",
    "Error budget tracking led to 3 reliability sprints that improved SLO to 99.95%. Feature teams had objective data — no more subjective debates. Burn rate alerts caught 4 incidents before they became SEV-1s. Engineering leadership adopted the model across all teams.",
    "This is core SRE philosophy — show you've read the Google SRE book. Mention the distinction between fast burn (big incident) and slow burn (chronic leak). T-Mobile will love this level of SRE maturity."
)

story += question_block(15,
    "How would you automate deployment of a log collector with sensitive tokens across hundreds of clusters?",
    "We needed to deploy a Fluentd log collector with Splunk HEC tokens to 300 clusters — doing it manually was taking 2 weeks and tokens were being hardcoded in ConfigMaps.",
    "Automate secure, scalable deployment with zero secret exposure and idempotent rollout capability.",
    "Used ArgoCD ApplicationSet to template the deployment across all clusters from a single Git source. Stored HEC tokens in AWS Secrets Manager per cluster. Used External Secrets Operator to sync secrets from Secrets Manager into Kubernetes Secrets automatically — no tokens in Git or ConfigMaps ever. Created a Helm chart for Fluentd with the token referenced as a Kubernetes Secret env var. ApplicationSet controller deployed to all 300 clusters in parallel with a maxUnavailable rollout policy. Added a validation job that confirmed log flow to Splunk post-deploy.",
    "Full deployment to 300 clusters completed in 45 minutes (vs 2 weeks manual). Zero tokens exposed in logs or Git history. External Secrets Operator auto-rotated tokens quarterly with zero manual effort. Compliance team approved the design for SOC2.",
    "Secret management + GitOps + multi-cluster is a perfect L3 combo. Knowing External Secrets Operator, Sealed Secrets, or Vault Agent Injector shows you're operating at senior level."
)

story += question_block(16,
    "CloudWatch alarms didn't trigger during a major outage. How do you debug this?",
    "We had a 45-minute partial outage where API error rates hit 35% — but CloudWatch alarms that should have fired at 5% error rate never triggered.",
    "Determine why alerting failed and prevent alert blind spots.",
    "Checked the alarm configuration: evaluation period was set to 5 data points of 5 minutes each = alarm only fires after 25 minutes of sustained breach. That's why it was late, not silent. Checked metric math: the error rate calculation used an average that was diluted by healthy endpoints — masked the failures on specific routes. Also found: alarm was in INSUFFICIENT_DATA state due to a brief CloudWatch agent gap. Investigated: agent was restarted during the outage window, causing a metric gap. Fixes: reduced evaluation to 2 of 3 periods; switched to percentile metrics (p99 error rate) per endpoint; added a dead man's switch alarm that fires if metrics stop flowing.",
    "Alarm latency reduced from 25 minutes to 4 minutes. Added a separate alarm for metric gaps (dead man's switch pattern). Implemented synthetic canaries (CloudWatch Synthetics) as a parallel alerting mechanism independent of the app metrics pipeline.",
    "Knowing the subtleties of CloudWatch alarm math, evaluation periods, and the dead man's switch pattern is expert-level. Interviewers will be impressed if you explain 'INSUFFICIENT_DATA' vs 'ALARM' states."
)

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 – SCRIPTING & AUTOMATION
# ═══════════════════════════════════════════════════════════════════════════════
story.append(section("SECTION 5: Python / Bash Scripting & Automation", "🐍"))
story.append(Spacer(1, 8))

story += question_block(17,
    "Describe automation you built that significantly reduced toil for your team.",
    "Our on-call engineers were spending 6+ hours per week manually responding to repetitive alerts — disk space warnings, certificate expiry notices, and stale pod restarts — that had known fixes.",
    "Automate the remediation of repetitive runbook tasks to reduce toil and free engineers for higher-value work.",
    "Built a Python-based 'auto-remediation bot' integrated with PagerDuty and Kubernetes API. For disk space: bot SSHed to node (via Paramiko), ran log rotation and Docker image cleanup. For cert expiry: bot triggered cert-manager renewal via CRD patch. For stale pods: bot checked restart count + OOM kill history and applied memory limit bump automatically. Bot posted actions to Slack with one-click override. Used Python kubernetes client library, boto3 for AWS actions, and PagerDuty Events v2 API. All actions logged to an audit DynamoDB table.",
    "Toil reduced by 70% — 6 hours/week → 1.5 hours/week. Auto-remediation successfully resolved 85% of the targeted alert types without human intervention. On-call satisfaction scores improved. The bot was extended to handle 12 additional runbook scenarios over 6 months.",
    "Mention the SRE toil definition: manual, repetitive, tactical, no enduring value. Show you're automating away the boring so humans focus on the complex. This directly speaks to T-Mobile's JD requirement."
)

story += question_block(18,
    "Secrets are appearing in Terraform logs. What is your fix and prevention plan?",
    "A developer noticed that database passwords were being printed in plain text in our GitHub Actions CI logs for Terraform deployments — a potential secret exposure.",
    "Immediately remediate the exposure and implement controls to prevent sensitive data appearing in any logs.",
    "Immediate: rotated all exposed credentials. Scrubbed GitHub Actions log history using the API. Identified root cause: terraform.tfvars containing secrets was being echoed in a pre-plan script. Also found: output blocks were logging sensitive values. Fixes applied: marked all sensitive outputs with 'sensitive = true' in Terraform (prevents console print). Moved secrets to AWS Secrets Manager and used the AWS provider's secretsmanager data source — values never appear in state or logs. Replaced tfvars secrets with environment variables prefixed TF_VAR_ (GitHub Actions masked secrets). Added a git-secrets pre-commit hook to block secret commits. Enabled Checkov in CI to scan Terraform for sensitive data patterns.",
    "Zero further secret exposure incidents. GitHub Actions now auto-masks any value registered as a secret. Checkov caught 3 additional potential issues in the first week. Compliance team validated the solution for SOC2 audit.",
    "T-Mobile handles customer data — security is paramount. Knowing 'sensitive = true' in Terraform outputs, and the difference between sensitive in state vs sensitive in logs, shows senior-level security awareness."
)

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 – REAL-TIME PRODUCTION SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════════
story.append(section("SECTION 6: Real-Time Production Scenarios (L3 Favorites)", "🔥"))
story.append(Spacer(1, 8))

story += question_block(19,
    "CPU utilization in your Kubernetes cluster is high even though workloads are low. Where do you look?",
    "At 3 AM, CPU alerts fired across 15 worker nodes showing 90%+ utilization despite application traffic being at 20% of normal.",
    "Identify the CPU consumer, rule out malicious activity, and restore normal CPU levels without impacting running workloads.",
    "Step 1: kubectl top nodes and kubectl top pods --all-namespaces — found a newly deployed monitoring agent consuming 40% CPU on every node. Step 2: kubectl describe pod on the agent — saw it was running a full cluster scan every 30 seconds (misconfigured interval). Step 3: Reduced scan interval to 5 minutes via ConfigMap patch. Step 4: Checked for crypto mining (ps aux, netstat for outbound connections) — clean. Step 5: Verified with metrics-server that CPU dropped after ConfigMap change. Step 6: Added CPU limit to the DaemonSet to cap noisy-neighbor impact.",
    "CPU normalized within 5 minutes of ConfigMap change. Added resource limits to all DaemonSets as a policy. Implemented Goldilocks (VPA recommendation tool) to right-size all workloads proactively.",
    "Mention: noisy neighbor problem, DaemonSet blast radius, and checking system namespace pods. Also: perf top, eBPF tools (bpftrace, pixie) for deep CPU profiling — shows senior Linux knowledge."
)

story += question_block(20,
    "Cross-namespace service communication is failing. What do you check first?",
    "A microservice in the 'payments' namespace couldn't reach a service in the 'auth' namespace — a change had been made to network policies the previous day.",
    "Restore cross-namespace communication while ensuring security policies remained intact.",
    "Step 1: Test connectivity: kubectl exec -it <pod> -n payments -- curl http://auth-service.auth.svc.cluster.local. Step 2: Check NetworkPolicies in the auth namespace — found a new policy with podSelector but no namespaceSelector, blocking cross-namespace traffic. Step 3: Added a namespaceSelector to the ingress rule allowing traffic from the payments namespace specifically. Step 4: Retested — connectivity restored. Step 5: Documented the NetworkPolicy change with a comment explaining the intent. Also checked: CoreDNS resolution (kubectl exec -- nslookup auth-service.auth), RBAC for service accounts, and Istio AuthorizationPolicies (we had a service mesh).",
    "Communication restored in 7 minutes. The NetworkPolicy change was well-intentioned (zero-trust posture) but lacked the cross-namespace allowance. We added a PR review requirement for any NetworkPolicy changes and built a connectivity testing framework using netshoot pods in CI.",
    "Cross-namespace DNS format (service.namespace.svc.cluster.local) is a test question favorite. Show you know NetworkPolicy selectors: podSelector, namespaceSelector, and ipBlock — and how to combine them."
)

story += question_block(21,
    "Lambda functions are timing out due to high latency in downstream APIs. What's your optimization?",
    "Our Lambda-based order processing functions were timing out (15-second limit hit) due to a downstream inventory API that started returning responses in 12-14 seconds.",
    "Reduce effective latency so Lambda functions complete within timeout while maintaining data consistency.",
    "Immediate: Increased Lambda timeout to 29 seconds as temporary relief (max is 15 min but we set a conservative ceiling). Then optimized: Implemented retry with exponential backoff and jitter in the Lambda code. Added a circuit breaker pattern — after 3 consecutive failures, Lambda returns a graceful degraded response and publishes to an SQS DLQ for later reprocessing. Moved to async pattern: Lambda publishes to SQS, a separate consumer Lambda processes with its own retry logic. Worked with the downstream team to add a cache layer (ElastiCache) in front of their API. Added X-Ray tracing to pinpoint which downstream call was slow.",
    "p99 latency dropped from 13 seconds to 800ms after ElastiCache was added. Timeout errors dropped to zero. The async/SQS pattern also improved throughput by 3x. X-Ray tracing is now standard for all Lambda functions.",
    "Lambda optimization is key for T-Mobile's serverless workloads. Mention: cold starts (provisioned concurrency), memory tuning for CPU allocation, connection reuse outside handler, and Lambda Power Tuning tool."
)

story += question_block(22,
    "You need to migrate Terraform state to S3 backend with DynamoDB locking. What steps do you take?",
    "Our team was using local Terraform state files — causing conflicts, no collaboration, and zero disaster recovery if a laptop was lost.",
    "Migrate state to S3 with DynamoDB locking with zero state corruption or team disruption.",
    "Step 1: Created S3 bucket with versioning enabled and server-side encryption. Created DynamoDB table with LockID as partition key. Step 2: Added backend config to Terraform: backend 'S3' with bucket, key, region, and dynamodb_table. Step 3: Ran 'terraform init -migrate-state' — Terraform prompts to copy local state to S3. Reviewed the migration prompt carefully. Step 4: Verified S3 had the state file and DynamoDB had no stale locks. Step 5: Deleted local .tfstate file only after confirming S3 version was correct. Step 6: Communicated to team — all engineers re-ran 'terraform init' to use new backend. Step 7: Added S3 bucket policy blocking public access and restricting to specific IAM roles.",
    "Migration completed with zero state corruption in under 30 minutes. Team immediately started collaborating without conflicts. One engineer accidentally left a stale lock — DynamoDB lock entry was manually deleted via console. Added a 'break-glass' runbook for stale lock scenarios.",
    "The exact CLI command 'terraform init -migrate-state' often comes up. Also mention: state locking prevents concurrent applies, and how to manually remove a stuck lock with terraform force-unlock <lock-id>."
)

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 – BEHAVIORAL & LEADERSHIP
# ═══════════════════════════════════════════════════════════════════════════════
story.append(section("SECTION 7: Behavioral & Leadership Questions (L3 Focus)", "🌟"))
story.append(Spacer(1, 8))

story += question_block(23,
    "Tell me about a time you mentored a junior engineer and the impact it had.",
    "A junior SRE joined our team who was strong in development but had no production operations experience. They were hesitant to take on-call shifts and afraid of making mistakes in prod.",
    "Help the engineer build confidence and competency in SRE practices to be ready for on-call within 3 months.",
    "Set up weekly 1:1s focused on their learning goals. Created a shadow on-call program — they shadowed me for 2 weeks, then I shadowed them for 2 weeks. Gave them ownership of a non-critical service's SLO and runbook documentation. Paired on a Terraform module project where they led and I reviewed. Introduced them to blameless postmortem culture to remove fear of mistakes. Gave specific, written feedback after every incident they participated in.",
    "Within 10 weeks, they were confident on-call and independently handled a SEV-2 incident. Their Terraform module was adopted by 3 other teams. They became the team's documentation champion. 6 months later, they were leading the onboarding of the next junior hire.",
    "L3 roles at T-Mobile involve mentoring. Show you invest in people. Use words: psychological safety, blameless culture, ownership, and structured feedback. These reflect T-Mobile's leadership principles."
)

story += question_block(24,
    "Describe a situation where you disagreed with a technical decision made by leadership. How did you handle it?",
    "Leadership decided to adopt a new orchestration tool (Nomad) to replace Kubernetes to 'simplify operations' — after I had just completed 6 months of deep K8s platform work and knew the ecosystem benefits.",
    "Advocate for the technically superior solution while respecting the decision-making process and maintaining team alignment.",
    "I requested a formal technical review meeting rather than debating informally. Prepared a data-driven comparison: K8s ecosystem maturity, CNCF support, team expertise, migration cost, and risk. Presented 3 scenarios with cost/risk analysis. Listened to the business reasons behind the Nomad preference — it was primarily vendor simplicity and a sales pitch. Proposed a 60-day pilot with defined success criteria before any migration commitment. Leadership agreed to the pilot.",
    "The pilot showed K8s outperformed on reliability metrics by 40%. Leadership reversed the decision based on data, not debate. More importantly, we established a formal RFC process for major technical decisions going forward — preventing future emotionally-driven decisions. My relationship with leadership improved because they saw I could advocate without being confrontational.",
    "L3 leaders disagree and commit. Show you used data, not emotion. Phrase it as: 'I expressed my concern through proper channels, presented evidence, and ultimately respected the process.' Never say you just complained."
)

story += question_block(25,
    "How do you balance reliability, velocity, and cost when they conflict?",
    "Our team was under pressure from product to deploy features faster, from finance to cut cloud costs, and from operations to improve reliability — all simultaneously with a 5-person SRE team.",
    "Create a framework that makes these trade-offs transparent and data-driven rather than political.",
    "Introduced error budgets as the reliability arbiter — when budget was healthy, we accelerated deployments; when it was burning, we froze features. Used cost-per-SLO-point analysis to justify reliability investments to finance (e.g., 'adding $5K/month in redundancy prevents $200K/month in outage costs'). Created a weighted priority matrix for the backlog. Implemented feature flags and canary deployments to allow velocity without reliability risk. Held quarterly reviews with all three stakeholders using dashboard data.",
    "Feature delivery velocity increased 25% through safer deployment practices. Cloud costs reduced 18% through right-sizing (enabled by better metrics). SLO improved from 99.5% to 99.9%. All three stakeholders reported higher satisfaction at the next quarterly review.",
    "This is a senior leadership question. Use the SRE trade-off language: 'error budget is the currency that buys reliability or velocity.' Show you can speak finance (ROI), product (velocity), and engineering (reliability) fluently."
)

story += question_block(26,
    "Tell me about a time you drove a culture change in your team.",
    "Our team had a blame culture — post-mortems were accusatory, engineers hid mistakes, and we kept making the same errors because people were afraid to report near-misses.",
    "Transform the team culture to blameless, psychologically safe, and continuously learning.",
    "Started with myself: in the next incident I owned, I publicly shared my own mistakes in the post-mortem. Rewrote the post-mortem template to focus on systems and processes, not people. Introduced 'near-miss' reporting with a policy that reporters were never disciplined. Set up monthly 'failure Fridays' — engineers voluntarily shared things that almost went wrong. Recognized engineers who surfaced problems, not just those who fixed them. Worked with management to remove any performance review language tied to incident count.",
    "Near-miss reporting increased 300% in 3 months — surfacing 12 issues before they became incidents. Post-mortem quality improved dramatically; action items completion rate went from 40% to 90%. Two engineers who had been disengaged became the most vocal advocates for the new culture. The model was adopted by two adjacent teams.",
    "Cultural impact is a strong L3 differentiator. Show you led change bottom-up AND top-down. Mention psychological safety (Amy Edmondson) if you want to impress — it signals senior-level thinking."
)

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 – QUESTIONS YOU SHOULD ASK
# ═══════════════════════════════════════════════════════════════════════════════
story.append(section("SECTION 8: Questions YOU Should Ask the Interviewer", "❓"))
story.append(Spacer(1, 10))

story.append(Paragraph(
    "Asking sharp, thoughtful questions at L3 is as important as answering them. "
    "It demonstrates strategic thinking, genuine interest, and senior-level curiosity. "
    "Pick 3-4 from below based on the conversation flow:",
    s("intro", fontSize=10, textColor=TEXT, leading=15, fontName="Helvetica",
      spaceAfter=10, alignment=TA_JUSTIFY)
))

questions_to_ask = [
    ("About the Platform",
     "What does the current Kubernetes fleet look like in terms of scale — number of clusters, "
     "nodes, and workloads — and where are the biggest reliability pain points today?"),
    ("About Tooling & Stack",
     "I saw GitLab, Argo, and Flux mentioned in the JD — are these all in active use, or is "
     "there a migration happening between GitOps tools? I'd love to understand the current state."),
    ("About Incidents",
     "How does T-Mobile currently handle incident command — do you use a formal ICS structure, "
     "and how is the on-call rotation structured for the SRE team?"),
    ("About Growth & Innovation",
     "What does the roadmap look like for the Container Platform team over the next 12 months — "
     "is the focus on scaling existing infrastructure, adopting new technologies, or both?"),
    ("About Culture",
     "How does the team currently handle the balance between reliability work and feature "
     "enablement? Is there a formal error budget or SLO framework in place?"),
    ("About AI Tooling",
     "I noticed the L2 questions mentioned AI tools like GitHub Copilot and Cursor — is the team "
     "actively adopting AI-assisted workflows, and is there an official stance on their use in infra work?"),
    ("About the Role",
     "What would success look like for this role at 30, 60, and 90 days? What's the most "
     "pressing problem you're hoping a new senior SRE will help solve?"),
    ("About Team Dynamics",
     "How is the team structured — is it a central SRE team serving multiple product teams, "
     "or are SREs embedded within specific engineering groups?"),
]

for category, question in questions_to_ask:
    row = [[
        Paragraph(category, s("qcat", fontSize=9, textColor=MAGENTA, fontName="Helvetica-Bold", leading=13)),
        Paragraph(f""{question}"", s("qtext", fontSize=10, textColor=TEXT, fontName="Helvetica-Oblique",
                   leading=14, alignment=TA_JUSTIFY))
    ]]
    t = Table(row, colWidths=[1.2*inch, 5.3*inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LINEBELOW", (0,0), (-1,-1), 0.3, colors.HexColor("#EEEEEE")),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#FFF0F5")),
        ("LEFTPADDING", (0,0), (0,0), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 3))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9 – CHEAT SHEET
# ═══════════════════════════════════════════════════════════════════════════════
story.append(section("SECTION 9: L3 Cheat Sheet & Power Phrases", "⚡"))
story.append(Spacer(1, 10))

# Power phrases table
story.append(Paragraph("🗣  Power Phrases That Signal Senior-Level Thinking", q_title))

phrases = [
    ("Trade-off thinking", '"I chose X over Y because at our scale, the trade-off between latency and consistency favored X."'),
    ("Data-driven decisions", '"We made this decision based on error budget burn rate data, not gut feel."'),
    ("Systems thinking", '"The root cause wasn\'t the pod crash — it was the lack of circuit breaking that allowed cascading failures."'),
    ("Blameless culture", '"Our post-mortem focused on system gaps, not individual mistakes."'),
    ("Mentorship impact", '"I structured the knowledge transfer so the team owned it, not me — that\'s how you scale."'),
    ("Business alignment", '"Every reliability investment I proposed was tied to an RTO/RPO requirement from the business."'),
    ("Proactive reliability", '"We caught this before it became an incident using burn rate alerts — not reactive paging."'),
    ("GitOps philosophy", '"The cluster state is declared in Git. If it\'s not in Git, it doesn\'t exist."'),
]

for phrase, example in phrases:
    row = [[
        Paragraph(phrase, s("ph", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold",
                   leading=13, backColor=MAGENTA)),
        Paragraph(example, s("phe", fontSize=9, textColor=TEXT, fontName="Helvetica-Oblique",
                   leading=13))
    ]]
    t = Table(row, colWidths=[1.5*inch, 5.0*inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (0,0), 8),
        ("LINEBELOW", (0,0), (-1,-1), 0.3, colors.HexColor("#EEEEEE")),
    ]))
    story.append(t)
    story.append(Spacer(1, 2))

story.append(Spacer(1, 14))

# Quick reference kubectl commands
story.append(Paragraph("⌨  Quick Reference: Must-Know Commands to Drop Naturally in Conversation", q_title))

cmds = [
    ("kubectl rollout undo deployment/<name> --to-revision=N", "Rollback to specific revision"),
    ("kubectl top pods --all-namespaces --sort-by=cpu", "Find CPU hogs across all namespaces"),
    ("kubectl debug node/<node> -it --image=busybox", "Debug at node level"),
    ("kubectl get events --sort-by='.lastTimestamp'", "Timeline of recent cluster events"),
    ("terraform state mv <old> <new>", "Rename resource in state without destroy"),
    ("terraform plan -out=tfplan && terraform show tfplan", "Safe plan review workflow"),
    ("aws ec2 describe-instances --filters 'Name=instance-state-name,Values=running'", "List all running EC2s"),
    ("kubectl exec -it <pod> -- curl http://svc.namespace.svc.cluster.local", "Test cross-namespace DNS"),
    ("kubectl drain <node> --ignore-daemonsets --delete-emptydir-data", "Safely evacuate a node"),
    ("helm rollback <release> <revision> -n <namespace>", "Helm rollback with namespace"),
]

cmd_data = [["Command", "Purpose"]]
for cmd, purpose in cmds:
    cmd_data.append([
        Paragraph(f'<font name="Courier" size="8" color="#1A237E">{cmd}</font>',
                  s("cd", fontSize=8, fontName="Courier", leading=11)),
        Paragraph(purpose, s("cp", fontSize=9, fontName="Helvetica", leading=13))
    ])

ct = Table(cmd_data, colWidths=[3.8*inch, 2.7*inch])
ct.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), DARK_GREY),
    ("TEXTCOLOR", (0,0), (-1,0), WHITE),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,0), 9),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, colors.HexColor("#F5F5FF")]),
    ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#DDDDDD")),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
]))
story.append(ct)

story.append(Spacer(1, 16))

# Final motivation box
final_data = [[
    Paragraph(
        "🚀  <b>You've Got This!</b><br/><br/>"
        "You've cleared L1 and L2 — that means T-Mobile already believes in your technical depth. "
        "The L3 round is about <b>leadership, architectural thinking, and cultural fit</b>. "
        "They want to see how you handle ambiguity, how you mentor others, and how you drive decisions "
        "with data.<br/><br/>"
        "Walk in as a <b>Senior Engineer who has done this at scale</b>, not a candidate who is hoping to. "
        "Speak in outcomes. Use numbers. Show empathy. Be blameless.<br/><br/>"
        "<font color='#E20074'><b>Good luck — come back and tell Claude you got the offer! 🎉</b></font>",
        s("final", fontSize=11, textColor=DARK_GREY, fontName="Helvetica",
          leading=18, alignment=TA_JUSTIFY)
    )
]]
ft = Table(final_data, colWidths=[6.5*inch])
ft.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FFF0F7")),
    ("TOPPADDING", (0,0), (-1,-1), 16),
    ("BOTTOMPADDING", (0,0), (-1,-1), 16),
    ("LEFTPADDING", (0,0), (-1,-1), 18),
    ("RIGHTPADDING", (0,0), (-1,-1), 18),
    ("BOX", (0,0), (-1,-1), 2, MAGENTA),
    ("ROUNDEDCORNERS", [8]),
]))
story.append(ft)

# ── Build PDF ──────────────────────────────────────────────────────────────────
output_path = "/mnt/user-data/outputs/TMobile_SRE_L3_Interview_Prep.pdf"

doc = BaseDocTemplate(
    output_path,
    pagesize=letter,
    leftMargin=0.65*inch,
    rightMargin=0.55*inch,
    topMargin=0.65*inch,
    bottomMargin=0.65*inch,
)

frame_cover = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0, rightPadding=0,
                    topPadding=0, bottomPadding=0)
frame_body  = Frame(0.65*inch, 0.65*inch, PAGE_W - 1.2*inch, PAGE_H - 1.3*inch,
                    id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[frame_cover], onPage=cover_page),
    PageTemplate(id="Body",  frames=[frame_body],  onPage=page_background),
])

from reportlab.platypus import NextPageTemplate
story.insert(0, NextPageTemplate("Body"))
story.insert(0, NextPageTemplate("Cover"))

doc.build(story)
print(f"PDF created: {output_path}")
