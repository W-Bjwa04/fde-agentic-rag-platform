# IT Service Desk Runbook

## Email Troubleshooting
If a user cannot send or receive email, confirm whether the issue affects one user or many users. Check network connectivity and the service status dashboard. For a single user, sign out and back in, verify mailbox quota, and test the web client. For widespread incidents, do not ask each user to reinstall software; escalate the suspected service incident.

## Laptop Performance
For a slow laptop, first check CPU, memory, storage free space, startup applications, operating system updates, and endpoint security scan status. Do not disable security agents as a troubleshooting shortcut. Escalate when hardware diagnostics report failure or repeated shutdowns continue after software remediation.

## Ticket Priority
P1: company-wide outage or critical security incident. P2: major team blocked with no workaround. P3: individual user blocked or degraded with limited workaround. P4: standard request, information seeking, or cosmetic issues.

## Account and Domain Lockouts
When a user encounters a 'Domain Account Locked' error message, verify their identity via their employee ID profile before performing any actions. Search for the account inside Active Directory (AD) and inspect the lockout source. If the lockout clears but immediately recurs, check for active active-sync profiles on mobile devices or stale mapped network drives cache. Do not unlock an account more than three times consecutively without escalating to the Security operations node.

## Software Deployment Failures
If an automated enterprise application push fails via the software center portal, instruct the user to restart the local SMS Agent Host service. Clear the local cache folder under Windows Configuration Manager if necessary. For persistent deployment error tracking codes, verify if the endpoint machine satisfies the minimal operating system build level required by the application framework. If the error code points to missing dependencies, manually install the framework prerequisites before retrying the deployment block.
