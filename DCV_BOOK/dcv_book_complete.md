% Make Data Cleaning Simple with DCV % Complete Language Documentation
% By Vignesh D, Aagash T, Keerthivasan V, Gowtham R

# Preface

DCV (Data Cleaning and Validation) is a declarative domain-specific
language designed specifically for structured data cleaning and
validation.

Unlike general-purpose programming languages, DCV intentionally limits
its scope. It focuses only on:

- Cleaning
- Validation
- Transformation
- Aggregation

This constraint produces clarity, predictability, and deterministic
behavior.

This document provides complete coverage of DCV 2.0 including:

- All commands
- All operators
- All expression types
- Case sensitivity rules
- Supported file formats
- Execution model
- Error taxonomy
- Internal architecture
- Full working case study
- Best practices
- Formal grammar overview

---

# Part I --- Language Philosophy

## 1. Why DCV Exists

Data cleaning in traditional systems is written procedurally:

```python
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df = df[df["age"] > 18]
```

As systems grow:

- Logic spreads across files
- Validation rules become implicit
- Error handling becomes inconsistent
- Auditing becomes difficult

DCV separates _intent_ from _implementation_.

```dcv
CAST age AS int
VALIDATE age > 18
```

This expresses rules clearly without exposing infrastructure complexity.

---

## 2. Core Design Principles

### Declarative

You describe what must be true.

### Deterministic

Same input + same script = same output.

### Row-Level

All transformations operate per row unless grouping is explicitly
defined.

### Vectorized

Internally executed using vector operations.

### Constrained

No loops. No dataset-level branching.

Constraint increases reliability.

---

# Part II --- Execution Model

When a DCV script runs, it passes through:

1.  Lexical Analysis
2.  Parsing
3.  Semantic Validation
4.  Execution Planning
5.  Vectorized Execution

## 1. Lexical Analysis

Script text is converted into tokens.

Example:

```dcv
CAST age AS int
```

Tokens:

- KEYWORD(CAST)
- IDENTIFIER(age)
- KEYWORD(AS)
- IDENTIFIER(int)

Keywords are normalized to uppercase, making them case-insensitive.

---

## 2. Parsing

Tokens are transformed into Abstract Syntax Tree (AST) nodes such as:

- Mode
- Load
- Cast
- Validate
- AddColumn
- GroupBy
- AggregateBlock

---

## 3. Semantic Validation

Checks include:

- Valid mode value
- GROUP_BY before AGGREGATE
- Valid aggregation functions
- Valid operator usage

Errors at this stage prevent execution.

---

## 4. Execution

Statements execute sequentially.

Each statement modifies the in-memory dataset.

---

# Part III --- Language Features

## Supported Input Formats

- .csv
- .txt
- .xlsx

## Supported Output Format

- .csv

## Case Sensitivity Rules

Element Case Sensitive

---

Keywords No
Column Names Yes
String Literals Yes
File Paths OS dependent

---

# Part IV --- Commands

## MODE

    MODE strict
    MODE tolerant

### strict

Stops execution on first error.

### tolerant

Removes invalid rows and continues.

Error:

    Invalid mode

---

## LOAD

    LOAD "file.csv"

Errors:

File not found:

    File not found → 'file.csv'

Unsupported format:

    Unsupported file format

---

## SAVE

    SAVE "output.csv"

Error:

    Unsupported file format

---

## TRIM

    TRIM column_name

Removes leading/trailing whitespace.

Error:

    Column not found

---

## REMOVE_NULLS

    REMOVE_NULLS column_name

Removes rows where column is null.

---

## CAST

    CAST column AS int
    CAST column AS float
    CAST column AS str

Strict mode:

    Invalid cast

Tolerant mode: Row removed.

---

## ADD_COLUMN

    ADD_COLUMN new_column = expression

Error:

    Invalid binary operator

---

## VALIDATE

    VALIDATE condition

Strict:

    Validation failed

---

## GROUP_BY

    GROUP_BY column1, column2

---

## AGGREGATE

    AGGREGATE
        SUM column AS alias
        AVG column AS alias
        COUNT column AS alias
        MIN column AS alias
        MAX column AS alias
    END

Errors:

Missing GROUP_BY:

    GROUP_BY must be defined before AGGREGATE

Unsupported aggregation:

    Unsupported aggregation function MEDIAN

---

# Part V --- Expressions

## Literal Types

- Integer: 10
- Float: 10.5
- String: "High"

## Identifiers

Column references such as:

    salary

## Unary Operators

- NOT

- - (numeric negation)

## Arithmetic Operators

- -

- -

- -

- /

## Comparison Operators

-

- \<

- =

- \<=

- ==

- !=

## Logical Operators

- AND
- OR

## IF Expression

    IF condition THEN value1 ELSE value2

Example:

```dcv
ADD_COLUMN category = IF salary > 50000 THEN "High" ELSE "Low"
```

## Function Calls

    FUNCTION_NAME(argument1, argument2)

Error:

    Unknown function 'XYZ'

---

# Part VI --- Error Taxonomy

## Syntax Errors

Unexpected character:

    Unexpected character '@'

Unterminated string:

    Unterminated string

## Runtime Errors

Invalid mode:

    Invalid mode

Unknown statement:

    Unknown statement

Invalid unary operator:

    Invalid unary operator

Invalid binary operator:

    Invalid binary operator

Invalid cast:

    Invalid cast

Validation failed:

    Validation failed

Column not found:

    Column not found

GROUP_BY missing:

    GROUP_BY must be defined before AGGREGATE

Unsupported aggregation:

    Unsupported aggregation function MEDIAN

Unknown function:

    Unknown function 'XYZ'

---

# Part VII --- End-to-End Case Study

Example script:

```dcv
MODE tolerant

LOAD "employees.csv"

TRIM name
CAST age AS int
REMOVE_NULLS salary

VALIDATE age >= 18

ADD_COLUMN annual_salary = salary * 12

GROUP_BY department

AGGREGATE
    SUM annual_salary AS total_payroll
    AVG annual_salary AS avg_salary
    COUNT age AS employee_count
END

SAVE "final_report.csv"
```

Execution Steps:

1.  Dataset loaded
2.  Whitespace cleaned
3.  Type converted
4.  Null rows removed
5.  Invalid rows filtered
6.  New column computed
7.  Aggregation performed
8.  Output written

---

# Part VIII --- Performance Considerations

- Vectorization improves speed.
- Filtering creates new DataFrame copies.
- GroupBy cost grows with unique groups.
- First run may be slower due to import overhead.

---

# Part IX --- Formal Grammar (Simplified)

    program       ::= statement+
    statement     ::= mode | load | save | trim | remove_nulls
                    | cast | add_column | validate | group_by | aggregate

    expression    ::= literal | identifier
                    | unary_op expression
                    | expression binary_op expression
                    | if_expression
                    | function_call

---

# Best Practices

1.  Define MODE first.
2.  Trim before casting.
3.  Cast before arithmetic.
4.  Validate after cleaning.
5.  Group only after validation.
6.  Use strict for compliance.
7.  Use tolerant for messy data.

---

# Closing

DCV is a focused language.

Its power comes not from complexity, but from clarity and constraint.

It exists to make data cleaning explicit, deterministic, and
maintainable.
