"""Safe expression calculator with persistent history."""
import argparse
import ast
import json
import math
from pathlib import Path
import operator

HISTORY = Path(__file__).with_name("history.json")
BIN_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
           ast.Mod: operator.mod, ast.Pow: operator.pow}
UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
FUNCTIONS = {"sqrt": math.sqrt, "abs": abs, "round": round}

def evaluate(node):
    if isinstance(node, ast.Expression): return evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool): return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
        left, right = evaluate(node.left), evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000: raise ValueError("Exponent is too large")
        result = BIN_OPS[type(node.op)](left, right)
        if not math.isfinite(float(result)): raise ValueError("Result is not finite")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS: return UNARY_OPS[type(node.op)](evaluate(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS and not node.keywords:
        return FUNCTIONS[node.func.id](*(evaluate(arg) for arg in node.args))
    raise ValueError("Only arithmetic, parentheses and sqrt/abs/round are allowed")

def calculate(expression):
    if len(expression) > 250: raise ValueError("Expression is too long")
    return evaluate(ast.parse(expression, mode="eval"))

def save_history(expression, result):
    entries = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    entries.append({"expression": expression, "result": result})
    HISTORY.write_text(json.dumps(entries[-100:], ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="SmartCalc · calculadora segura")
    parser.add_argument("expression", nargs="?")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--history", action="store_true")
    args = parser.parse_args()
    if args.history:
        print(HISTORY.read_text(encoding="utf-8") if HISTORY.exists() else "Sin operaciones todavía.")
        return
    if args.interactive:
        print("SmartCalc · escribe una expresión o 'salir'")
        while True:
            expression = input("calc> ").strip()
            if expression.lower() in {"salir", "exit", "quit"}: break
            try:
                result = calculate(expression); save_history(expression, result); print(f"= {result:g}")
            except (ValueError, SyntaxError, ArithmeticError, TypeError) as error: print(f"Error: {error}")
        return
    if not args.expression: parser.error("escribe una expresión o usa --interactive")
    try:
        result = calculate(args.expression); save_history(args.expression, result); print(f"{args.expression} = {result:g}")
    except (ValueError, SyntaxError, ArithmeticError, TypeError) as error: parser.error(str(error))

if __name__ == "__main__": main()

