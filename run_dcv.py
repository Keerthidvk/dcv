import time
start = time.time()

import sys
from dcv.core.lexer import Lexer
from dcv.core.parser import Parser
from dcv.core.executor import Executor
from dcv.errors.base_error import DCVError


def run_script(path):
    with open(path) as f:
        source = f.read()

    tokens = Lexer(source).tokenize()
    # print("\nTOKENS:")
    # for t in tokens:
    #     print(t.line,t.type, t.value)
    program = Parser(tokens).parse()
    Executor(program).execute()

    print("DCV execution completed successfully.")


if __name__ == "__main__":
    try:
        run_script(sys.argv[1])
    except DCVError as e:
        print("DCV execution failed:")
        print(e)
#print("Execution time:", time.time() - start)