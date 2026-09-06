"""Print this machine's optional DKYJ MCP entry. Contains paths, never credentials."""
import json
from pathlib import Path
from platform_paths import project_python
root=Path(__file__).resolve().parents[1]
print(json.dumps({'mcpServers':{'dkyj-director':{'command':str(project_python(root)),'args':[str(root/'scripts/agent_server.py')]}}},ensure_ascii=False,indent=2))
