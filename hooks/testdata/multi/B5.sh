python3 - <<'EOF'
import subprocess
subprocess.run(["acli","jira","workitem","assign","--key","TP-1","--assignee","@me"])
EOF
