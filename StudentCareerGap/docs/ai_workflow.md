# AI Workflow Document

## Overview

SkillPath AI uses a transparent decision engine rather than a paid external LLM. This keeps the app functional offline and compliant with free-only requirements for the hackathon.

## Recommendation logic

For each role, the application compares a student's self-reported skill levels to the role requirement profile using the formula below:

Role Match Percentage = (Sum of skill weights x normalized proficiency) / (Sum of all required skill weights) x 100

with normalized proficiency capped at 1, computed as:

Student proficiency / required proficiency, with a maximum of 1.

## Input categories used

- Academic profile
- Preferred job role
- Skill ratings (0-5)
- Study availability and learning duration
- Selected role requirements and hidden skill priorities

## Prompt templates

The app does not call an external AI API. Instead, it applies explanation templates for:

- recommendation rationale
- gap explanation
- next-step guidance
- practical project suggestions

## Responsible AI practices

- No private student data is exposed publicly.
- All recommendations are clearly labeled as rule-based outputs.
- Self-reported skill ratings are not treated as objective verification.
- Resource links are curated and stored locally.
- The app keeps an AI usage and decision log with methodology and prompt templates.
