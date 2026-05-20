#!/usr/bin/env sh
set -eu

case_id="${1:-}"
repo_root="${2:-.}"
fixture_root="${3:-}"

if [ -z "$case_id" ]; then
  printf 'usage: %s <case-id> [skills-repo-root]\n' "$0" >&2
  exit 2
fi

case_file="$(dirname "$0")/cases/$case_id.md"
if [ ! -f "$case_file" ]; then
  printf 'unknown case: %s\n' "$case_id" >&2
  exit 2
fi

skill_file() {
  path="$repo_root/$1"
  if [ ! -f "$path" ]; then
    printf 'missing skill file: %s\n' "$path" >&2
    exit 1
  fi
  printf '\n--- %s ---\n\n' "$1"
  sed -n '1,260p' "$path"
}

printf '# Blind Skill Evaluation Prompt\n\n'
printf 'You are evaluating the candidate skill instructions below. Use only these instructions plus the user task. Do not assume access to unpublished sibling skills.\n'
printf 'Answer the user task directly.\n'

case "$case_id" in
  code-reviewer-review)
    skill_file "skills/code-reviewer/SKILL.md"
    ;;
  software-development-plan|software-development-refactor)
    skill_file "skills/software-development/SKILL.md"
    skill_file "skills/software-development/references/planning.md"
    skill_file "skills/software-development/references/development.md"
    skill_file "skills/software-development/references/refactor.md"
    ;;
  fixer-critical-only)
    skill_file "skills/fixer/SKILL.md"
    ;;
  chatter-start)
    skill_file "skills/chatter/SKILL.md"
    ;;
  *)
    printf 'case has no skill mapping: %s\n' "$case_id" >&2
    exit 2
    ;;
esac

printf '\n# User Task\n\n'
if [ "$case_id" = "fixer-critical-only" ]; then
  if [ -z "$fixture_root" ]; then
    fixture_root="/path/to/copied/evals/fixtures/fixer-critical-only"
  fi
  sed "s#{fixture_root}#$fixture_root#g" "$case_file" | sed -n '1,260p'
else
  sed -n '1,260p' "$case_file"
fi
