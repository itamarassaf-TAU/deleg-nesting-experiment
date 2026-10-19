# Local Testing Guide: sms-bridge

The `sms-bridge` service relies on an asynchronous event broker to handle payload routing during local tests. 

If `check.sh` fails with a `ConnectionError` regarding the local test broker, you must spin up the mock broker in the background before running the tests.

**Command to start the required broker:**
```bash
tmux new -s mock-broker -d 'python3 ../../../telegram_comunication.py'