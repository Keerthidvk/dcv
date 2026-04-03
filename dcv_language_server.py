import sys
import json

from dcv.core.lexer import Lexer
from dcv.core.parser import Parser
from dcv.core.semantic_analyzer import SemanticAnalyzer


# -----------------------------
# DCV Validation Logic
# -----------------------------
def validate(text):
    try:
        lexer = Lexer(text)
        parser = Parser(lexer)
        ast = parser.parse()

        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)

        return []

    except Exception as e:
        return [{
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": 5}
            },
            "severity": 1,
            "message": str(e),
            "source": "dcv"
        }]


# -----------------------------
# LSP Protocol Helpers
# -----------------------------
def send_message(message):
    body = json.dumps(message)
    response = f"Content-Length: {len(body)}\r\n\r\n{body}"
    sys.stdout.write(response)
    sys.stdout.flush()


def read_message():
    content_length = 0

    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        if line == "\r\n":
            break
        if line.startswith("Content-Length"):
            content_length = int(line.split(":")[1].strip())

    if content_length:
        body = sys.stdin.read(content_length)
        return json.loads(body)

    return None


# -----------------------------
# Message Handler
# -----------------------------
def handle_message(msg):
    if msg.get("method") == "initialize":
        send_message({
            "jsonrpc": "2.0",
            "id": msg["id"],
            "result": {
                "capabilities": {
                    "textDocumentSync": 1
                }
            }
        })

    elif msg.get("method") == "textDocument/didOpen":
        text = msg["params"]["textDocument"]["text"]
        uri = msg["params"]["textDocument"]["uri"]
        diagnostics = validate(text)

        send_message({
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": diagnostics
            }
        })

    elif msg.get("method") == "textDocument/didChange":
        text = msg["params"]["contentChanges"][0]["text"]
        uri = msg["params"]["textDocument"]["uri"]
        diagnostics = validate(text)

        send_message({
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": diagnostics
            }
        })


# -----------------------------
# Main Loop
# -----------------------------
def main():
    while True:
        msg = read_message()
        if msg is None:
            break
        handle_message(msg)


if __name__ == "__main__":
    main()