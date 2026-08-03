#!/usr/bin/env bash
# detect_provider.sh — prints the best available issue-tracker provider.
#
# Exit 0 always; stdout is one of: gitlab, github, jira, none
# Probe order: git remote (repo context) first, then installed tools, then JIRA env.

set -euo pipefail

# 1. Infer from git remote origin — repo context beats installed-tool defaults.
if remote=$(git remote get-url origin 2>/dev/null); then
  if echo "$remote" | grep -q "github\.com"; then
    if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
      echo "github"; exit 0
    fi
  elif echo "$remote" | grep -qE "gitlab\.com|gitlab\."; then
    if command -v glab &>/dev/null && glab auth status &>/dev/null 2>&1; then
      echo "gitlab"; exit 0
    fi
  fi
fi

# 2. Fall back to whichever CLI tool is authenticated.
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
