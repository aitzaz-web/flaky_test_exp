import ast
import astor

class InstrumentationTransformer(ast.NodeTransformer):
    """
    A transformer that modifies Python test functions by:
    1. Inserting random seed initialization wherever random number generation is detected.
    2. Adding logging statements before an assertion on a specified line.
    """

    def __init__(self, test_name, assertion_line):
        """
        Initializes the transformer with the target function name and assertion line.

        Parameters:
        - test_name (str): The name of the function where assertion logging should be applied.
        - assertion_line (int): The line number of the assertion to be logged.
        """
        self.test_name = test_name
        self.assertion_line = assertion_line
        self.functions_with_random = {}  # Stores functions that use randomness

    def visit_FunctionDef(self, node):
        """
        Visits function definitions to:
        - Detect random number generation.
        - Apply assertion logging if the function matches the target test function.

        Parameters:
        - node (ast.FunctionDef): The function definition node in the AST.

        Returns:
        - ast.FunctionDef: The modified function node.
        """
        print(f"Processing function: {node.name}")

        # Reset tracking variables for each function
        self.uses_random = False
        self.uses_numpy = False
        self.uses_torch = False
        self.uses_tensorflow = False

        # Check for random number generation within the function body
        for stmt in node.body:
            self._check_random_usage(stmt)

        # Store functions that use randomness for later seed insertion
        if any([self.uses_random, self.uses_numpy, self.uses_torch, self.uses_tensorflow]):
            self.functions_with_random[node.name] = (
                self.uses_random, self.uses_numpy, self.uses_torch, self.uses_tensorflow
            )

        new_body = []

        # Apply assertion logging only in the specified function
        if node.name == self.test_name:
            for stmt in node.body:
                transformed_stmt = self.visit(stmt)
                if isinstance(transformed_stmt, list):
                    new_body.extend(transformed_stmt)
                else:
                    new_body.append(transformed_stmt)
        else:
            new_body.extend(node.body)  # Keep the function unchanged if it's not the target

        node.body = new_body
        return node

    def visit_Assert(self, node):
        """
        Visits assertion statements and adds logging before the assertion
        if it is located on the specified line.

        Parameters:
        - node (ast.Assert): The assertion statement node.

        Returns:
        - List[ast.Expr] or ast.Assert: A list containing log statements followed by the assertion,
          or the unmodified assertion if it is not on the specified line.
        """
        if isinstance(node.test, ast.Compare) and node.lineno == self.assertion_line:
            left = node.test.left
            right = node.test.comparators[0]

            log_statements = []

            def make_log(var):
                """Creates a print statement logging the value of a variable or expression."""
                if isinstance(var, ast.Name):
                    return ast.Expr(ast.Call(
                        func=ast.Name(id='print', ctx=ast.Load()),
                        args=[ast.Constant(value=f'log>> {var.id}:'), var],
                        keywords=[]
                    ))
                elif isinstance(var, ast.Call) or isinstance(var, ast.Subscript):
                    return ast.Expr(ast.Call(
                        func=ast.Name(id='print', ctx=ast.Load()),
                        args=[ast.Constant(value=f'log>> {astor.to_source(var).strip()}:'), var],
                        keywords=[]
                    ))

            log_statements.append(make_log(left))
            log_statements.append(make_log(right))

            return log_statements + [node]

        return node

    def _check_random_usage(self, node):
        """
        Recursively checks if a function contains random number generation
        and updates the appropriate tracking flags.

        Parameters:
        - node (ast.AST): The AST node to analyze.
        """
        if isinstance(node, ast.Call):  # Detect function calls
            func = node.func
            if isinstance(func, ast.Attribute):
                module_name = getattr(func.value, "id", None)

                if module_name == "random":
                    self.uses_random = True
                    print(f"Detected random usage: {module_name}.{func.attr}")

                elif module_name in {"np", "numpy"}:
                    self.uses_numpy = True
                    print(f"Detected NumPy usage: {module_name}.{func.attr}")

                elif isinstance(func.value, ast.Attribute):
                    submodule_name = getattr(func.value.value, "id", None)
                    if submodule_name in {"np", "numpy"} and func.value.attr == "random":
                        self.uses_numpy = True
                        print(f"Detected NumPy random usage: {submodule_name}.{func.value.attr}.{func.attr}")

        # Recursively analyze child nodes
        for child in ast.iter_child_nodes(node):
            self._check_random_usage(child)

import os
def instrument_test_file(file_path, test_name, assertion_line, output_file=None):
    """
    Parses a Python test file, modifies the AST, and saves the instrumented version.

    Parameters:
    - file_path (str): The path to the original test file.
    - test_name (str): The name of the test function.
    - assertion_line (int): The assertion line number.
    - output_file (str, optional): Path to save the instrumented test file.
    """
    with open(file_path, "r") as source:
        tree = ast.parse(source.read())

    transformer = InstrumentationTransformer(test_name, assertion_line)
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)

    # Convert the modified AST back to source code
    modified_code = astor.to_source(transformed_tree)

    # Determine the output file path
    if output_file is None:
        output_file = f"instrumented_{os.path.basename(file_path)}"  # Save in script directory

    with open(output_file, "w") as output:
        output.write(modified_code)

    print(f"✅ Instrumented file saved as: {output_file}")



# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python static_instrumentation.py <file_path> <test_name> <assertion_line>")
        sys.exit(1)

    file_path = sys.argv[1]
    test_name = sys.argv[2]
    assertion_line = int(sys.argv[3])

    instrument_test_file(file_path, test_name, assertion_line)