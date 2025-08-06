import json

parsed_json = []

with open('pingapp.log') as log_file:
    for line in log_file:
        if line.strip():
            parsed_json.append(json.loads(line))

print(parsed_json)
print(json.dumps(parsed_json, indent=4))