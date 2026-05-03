# Contributing to Quantum Modeling Showcase

First of all, thank you for your interest in contributing! <3

To keep the project consistent, readable, and valuable for the community, please follow the guidelines below.

## Contribution Philosophy

We aim for contributions that are:

* **Structured** - clearly organized and documented
* **Insightful** - not just code, but also design reasoning
* **Comparable** - enabling analysis across different approaches
* **Reproducible** - others should be able to understand and run your work

## What You Can Contribute

You can contribute:

* New quantum system modeling examples
* Alternative modeling approaches for existing problems
* Improvements to documentation
* Fixes or refinements to existing examples

## Adding a New Example

All examples must follow the repository structure.

### 1. Create a new folder

Inside `/projects/`, create a folder using **kebab-case**:

```id="ex1"
projects/your-project-name/
```

### 2. Use the template

Copy the template from:

```id="ex2"
templates/example-template/
```

### 3. Required structure

Your example must include:

```id="ex3"
your-project-name/
├── README.md
├── diagrams/
├── code/
└── assets/ (optional)
```

###  Contribution Workflow

1. Fork the repository
2. Create a new branch:

   ```
   feature/your-project-name
   ```
3. Add your example following the guidelines
4. Commit your changes with clear messages
5. Open a Pull Request

## Guidelines

To keep the repository organized, useful, and accessible for future contributors, please follow these guidelines:

### Modeling

- Be explicit about your modeling choices.
- Avoid unnecessary complexity.
- Prefer clarity over excessive completeness.
- If using custom abstractions or notations, explain them clearly.

### Code

- Ensure that the code is readable and documented.
- Include clear instructions for execution.
- Avoid unnecessary dependencies whenever possible.
- Provide example inputs and outputs when relevant.

### Diagrams

- Make sure diagrams are legible and well-structured.
- Use consistent naming conventions.
- Prefer vector formats (.svg, .pdf) whenever possible.
- If using UML or related variants, describe any custom notation adopted.

## Review Process

All contributions will be reviewed to ensure:

* Consistency with repository standards
* Clarity and quality of explanation
* Relevance to quantum system modeling

Feedback may be provided — please be open to iteration.