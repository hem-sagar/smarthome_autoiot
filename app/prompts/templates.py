ZERO_SHOT_TEMPLATE = '''
You are a smart-home rule parser.
Convert the command into JSON with:
location, device, action, condition, confidence, uncertain_reason.
Use only supported devices and actions.
Command: "{command}"
Catalog:
{catalog}
Return JSON only.
'''

ONE_SHOT_TEMPLATE = '''
You are a smart-home rule parser.

Example:
Command: "Turn on living room light when motion is detected at night"
JSON:
{{"location":"living_room","device":"light","action":"turn_on","condition":"motion == 1 AND time_bucket == \'night\'","confidence":0.95,"uncertain_reason":""}}

Now parse:
Command: "{command}"
Catalog:
{catalog}
Return JSON only.
'''

VERIFIER_TEMPLATE = '''
You are checking whether a generated smart-home rule is supported.
Review the command, catalog, and current JSON rule.
If it is invalid, return a safer repaired JSON rule using only supported values.
Also return:
- hallucination_type
- confidence
- explanation
- fixed

Command: "{command}"
Catalog:
{catalog}
Current JSON:
{rule_json}

Return JSON only.
'''

RESOLVER_TEMPLATE = '''
You are explaining a remaining smart-home automation issue to an end user.
Given the command, current rule, and issue, return JSON with:
- explanation
- safe_resolution
- confidence
- uncertain_reason

Command: "{command}"
Rule JSON:
{rule_json}
Issue: "{issue}"

Return JSON only.
'''
