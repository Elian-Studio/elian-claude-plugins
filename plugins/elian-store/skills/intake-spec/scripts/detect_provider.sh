#!/usr/bin/env bash
# detect_provider.sh — prints the best available issue-tracker provider.
#
# Exit 0 always; stdout is one of: gitlab, github, jira, none
# Probe order: GitLab first (glab), GitHub second (gh), JIRA env third, none.

set -euo pipefail

if command -v glab &>/dev/null && glab auth status &>/dev/null 2>&1; then
  echo "gitlab"
  exit 0
fi

if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
  echo "github"
  exit 0
fi

# JIRA: presence of Atlassian MCP env var or common credential files
if [[ -n "${ATLASSIAN_API_TOKEN:-}" ]] || \
   [[ -f "${HOME}/.claude/.atlassian" ]] || \
   [[ -n "${JIRA_API_TOKEN:-}" ]]; then
  echo "jira"
  exit 0
fi

echo "none"
