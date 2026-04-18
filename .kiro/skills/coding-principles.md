# Coding Principles Skill

Software engineering best practices and design principles to follow when writing or reviewing code.

## SOLID Principles

**Single Responsibility** - Each class/module has one reason to change
- One class = one job
- Separate concerns into different modules

**Open/Closed** - Open for extension, closed for modification
- Use inheritance, interfaces, composition
- Don't modify existing code to add features

**Liskov Substitution** - Subtypes must be substitutable for base types
- Child classes shouldn't break parent class contracts
- Maintain expected behavior

**Interface Segregation** - Clients shouldn't depend on unused interfaces
- Many specific interfaces > one general interface
- Don't force implementations of unused methods

**Dependency Inversion** - Depend on abstractions, not concretions
- High-level modules shouldn't depend on low-level modules
- Both should depend on abstractions

## Core Principles

**DRY (Don't Repeat Yourself)**
- Extract duplicated code into functions/classes
- Use inheritance or composition for shared behavior
- Single source of truth for logic and data

**Separation of Concerns**
- Business logic ≠ data access ≠ presentation
- Each layer has clear responsibility
- Minimize cross-layer dependencies

**Error Handling**
- Wrap risky operations in try-catch
- Meaningful error messages with context
- Fail gracefully with fallbacks
- Validate inputs at boundaries
- Log errors appropriately

**Naming Conventions**
- Clear, descriptive names
- Functions: verbs (get_user, calculate_total)
- Classes: nouns (UserManager, PaymentProcessor)
- Booleans: is/has/can prefix
- Avoid abbreviations unless standard

## Anti-Patterns to Avoid

**God Objects** - Classes doing too much
- Split into smaller, focused classes
- Each class should have single responsibility

**Tight Coupling** - Components too dependent on each other
- Use dependency injection
- Program to interfaces, not implementations

**Magic Numbers** - Hardcoded values without context
- Use named constants
- Configuration files for environment-specific values

**Deep Nesting** - Too many nested if/for statements
- Extract to functions
- Use early returns/guard clauses
- Flatten logic

**Long Functions** - Functions >50 lines
- Extract logical blocks into separate functions
- Each function does one thing well

**Dead Code** - Unused imports, variables, functions
- Remove immediately
- Don't comment out - use version control

## Code Organization

**File Structure**
- Logical grouping by feature/domain
- Clear module boundaries
- Consistent naming patterns

**Function Length**
- Keep functions short (<50 lines)
- One level of abstraction per function
- Extract complex logic

**Class Design**
- Small, focused classes
- Composition over inheritance
- Minimize public interface

## Testability

- Pure functions when possible (no side effects)
- Dependency injection for mocking
- Avoid global state
- Clear input/output contracts
- Separate I/O from logic

## Review Checklist

- [ ] Each class/function has single responsibility
- [ ] No code duplication
- [ ] Proper error handling with try-catch
- [ ] Clear, descriptive names
- [ ] No magic numbers or hardcoded values
- [ ] Functions <50 lines
- [ ] No deep nesting (>3 levels)
- [ ] No unused imports or dead code
- [ ] Proper separation of concerns
- [ ] Code is testable

## When Reviewing Code

1. Check for principle violations
2. Identify anti-patterns
3. Suggest specific improvements with rationale
4. Prioritize by impact (critical > major > minor)
5. Balance ideal design with practical constraints
