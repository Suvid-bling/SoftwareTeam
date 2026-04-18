# Sequence UML Diagrams — SdeTeam (MetaGPT)

## 1. Team Initialization & Setup

```mermaid
sequenceDiagram
    actor User
    participant Team
    participant Ctx as Context
    participant Cfg as Config
    participant Env as Environment
    participant Role

    User->>Team: Team(context, roles, ...)
    Team->>Ctx: Context() or use provided
    Team->>Cfg: Config.default()
    Cfg-->>Ctx: config attached

    alt use_mgx = True
        Team->>Env: MGXEnv(context=ctx)
    else use_mgx = False
        Team->>Env: Environment(context=ctx)
    end

    Team->>Team: hire(roles)
    Team->>Env: add_roles(roles)

    loop For each role
        Env->>Role: role.context = ctx
        Env->>Role: role.set_env(env)
        Role->>Env: env.set_addresses(role, role.addresses)
        Role->>Role: set_actions(self.actions)
        loop For each action
            Role->>Role: _init_action(action)
            Note right of Role: action.set_context(ctx)<br/>action.set_llm(llm)<br/>action.set_prefix(prefix)
        end
    end

    User->>Team: invest(investment)
    Team->>Ctx: cost_manager.max_budget = investment
```

## 2. Team.run() — Main Execution Loop

```mermaid
sequenceDiagram
    actor User
    participant Team
    participant CM as CostManager
    participant Env as Environment
    participant Role

    User->>Team: await run(n_round=3, idea="Build X")
    Team->>Team: run_project(idea)
    Team->>Env: publish_message(Message(content=idea))
    Note over Env: Initial requirement<br/>distributed to roles

    loop While n_round > 0
        Team->>Env: is_idle?
        alt All roles idle
            Env-->>Team: True
            Note over Team: Break loop
        else Roles have work
            Env-->>Team: False
            Team->>CM: check total_cost < max_budget
            alt Budget exceeded
                CM-->>Team: NoMoneyException
            else Budget OK
                Team->>Env: await run()
                Note over Env: Execute all non-idle<br/>roles in parallel
                Env-->>Team: round complete
                Team->>Team: n_round -= 1
            end
        end
    end

    Team->>Env: archive(auto_archive)
    Env-->>Team: env.history
    Team-->>User: return history
```

## 3. Environment.run() — Parallel Role Dispatch

```mermaid
sequenceDiagram
    participant Env as Environment
    participant R1 as Role A
    participant R2 as Role B
    participant R3 as Role C
    participant Async as asyncio

    Env->>Env: run(k=1)

    Env->>R1: is_idle?
    R1-->>Env: False
    Env->>R2: is_idle?
    R2-->>Env: True (skip)
    Env->>R3: is_idle?
    R3-->>Env: False

    Note over Env: Collect futures for<br/>non-idle roles

    Env->>Async: gather(R1.run(), R3.run())

    par Role A executes
        Async->>R1: await run()
        R1-->>Async: Message or None
    and Role C executes
        Async->>R3: await run()
        R3-->>Async: Message or None
    end

    Async-->>Env: All futures resolved
```

## 4. Role.run() — Full Observe-React Cycle

```mermaid
sequenceDiagram
    participant Caller
    participant Role
    participant MsgBuf as MessageQueue
    participant Mem as Memory
    participant RC as RoleContext

    Caller->>Role: await run(with_message)

    opt with_message provided
        Role->>Role: Wrap as Message(cause_by=UserRequirement)
        Role->>MsgBuf: push(msg)
    end

    Note over Role: === _observe() ===
    Role->>MsgBuf: pop_all()
    MsgBuf-->>Role: raw news[]

    Role->>RC: get watch set
    Role->>Role: Filter: cause_by in watch<br/>OR name in send_to
    Role->>Mem: add_batch(filtered news)
    Role->>Role: latest_observed_msg = news[-1]

    alt No news
        Role-->>Caller: None (suspend)
    else Has news
        Note over Role: === react() ===
        Role->>Role: await react()

        alt react_mode = REACT or BY_ORDER
            Role->>Role: await _react()
        else react_mode = PLAN_AND_ACT
            Role->>Role: await _plan_and_act()
        end

        Role->>Role: set_todo(None), state = -1
        Role->>Role: publish_message(rsp)
        Role-->>Caller: return rsp
    end
```

## 5. Role._react() — Think-Act Loop (REACT / BY_ORDER)

```mermaid
sequenceDiagram
    participant Role
    participant RC as RoleContext
    participant LLM as BaseLLM
    participant Act as Action
    participant Mem as Memory

    Note over Role: actions_taken = 0

    loop While actions_taken < max_react_loop
        Note over Role: === _think() ===

        alt Only 1 action
            Role->>RC: set_state(0), todo = actions[0]
        else react_mode = BY_ORDER
            Role->>RC: state += 1
            Role->>RC: todo = actions[state]
        else react_mode = REACT (multi-action)
            Role->>Role: Build STATE_TEMPLATE prompt<br/>(history + available states)
            Role->>LLM: await aask(prompt)
            LLM-->>Role: next_state (number or -1)
            Role->>RC: set_state(next_state)
            alt next_state = -1
                Note over Role: No more actions → break
            end
        end

        alt has_todo = False
            Note over Role: Break loop
        else has_todo = True
            Note over Role: === _act() ===
            Role->>Act: await todo.run(rc.history)
            Act-->>Role: response

            alt response is ActionOutput/ActionNode
                Role->>Role: msg = AIMessage(content, instruct_content)
            else response is Message
                Role->>Role: msg = response
            else response is str
                Role->>Role: msg = AIMessage(content=response)
            end

            Role->>Mem: memory.add(msg)
            Note over Role: actions_taken += 1
        end
    end

    Role-->>Role: return rsp (last action's message)
```

## 6. Message Publishing & Routing

```mermaid
sequenceDiagram
    participant Sender as Role (Sender)
    participant Env as Environment
    participant Hist as History Memory
    participant R1 as Role A
    participant R2 as Role B
    participant BufA as A.msg_buffer
    participant BufB as B.msg_buffer

    Sender->>Sender: publish_message(msg)
    Note over Sender: Resolve ROUTE_TO_SELF<br/>Set sent_from

    alt All recipients = self
        Sender->>Sender: put_message(msg) → own buffer
    else Has external recipients
        Sender->>Env: publish_message(msg)

        loop For each (role, addrs) in member_addrs
            Env->>Env: is_send_to(msg, addrs)?

            alt Match: Role A
                Env->>R1: put_message(msg)
                R1->>BufA: push(msg)
            end
            alt Match: Role B
                Env->>R2: put_message(msg)
                R2->>BufB: push(msg)
            end
            alt No match
                Note over Env: Skip
            end
        end

        Env->>Hist: history.add(msg)
    end
```

## 7. Action.run() → LLM Call Chain

```mermaid
sequenceDiagram
    participant Role
    participant Act as Action
    participant Node as ActionNode
    participant LLM as BaseLLM
    participant API as OpenAI API

    Role->>Act: await run(history)

    alt action.node exists
        Act->>Act: _run_action_node(history)
        Act->>Act: Build context from history messages
        Act->>Node: await fill(req=context, llm=self.llm)

        Node->>Node: set_llm(llm), set_context(req)

        alt mode = simple (default)
            Node->>Node: compile(context, schema, mode)
            Note over Node: Build prompt from<br/>instruction + example + schema
            Node->>LLM: await aask(prompt) or _aask_v1(prompt, ...)
        else mode = code_fill
            Node->>LLM: await aask(context)
            Note over Node: Extract code block
        else mode = xml_fill
            Node->>Node: xml_compile(context)
            Node->>LLM: await aask(context)
            Note over Node: Parse XML tags
        end

        LLM->>LLM: Build messages[]<br/>(system_msg + user_msg)
        LLM->>LLM: compress_messages()
        LLM->>API: await _achat_completion(messages)
        API-->>LLM: ChatCompletion response
        LLM->>LLM: get_choice_text(resp)
        LLM->>LLM: cost_manager.update_cost(tokens, model)
        LLM-->>Node: response text

        Node->>Node: Parse into instruct_content
        Node-->>Act: ActionNode (with content + instruct_content)
        Act-->>Role: ActionNode

    else No node — subclass implementation
        Act->>Act: Custom run() logic
        Act->>LLM: await _aask(prompt)
        LLM->>API: await _achat_completion(messages)
        API-->>LLM: response
        LLM-->>Act: response text
        Act-->>Role: result (str / Message / ActionOutput)
    end
```

## 8. Plan-and-Act Strategy (Planner Lifecycle)

```mermaid
sequenceDiagram
    participant Role
    participant Planner
    participant WP as WritePlan
    participant AR as AskReview
    participant Plan
    participant LLM as BaseLLM
    participant WMem as Working Memory

    Role->>Role: _plan_and_act()
    Role->>Planner: current_task?

    alt No plan goal yet
        Role->>Role: goal = memory.get()[-1].content
        Role->>Planner: await update_plan(goal)

        loop Until plan confirmed
            Planner->>Planner: get_useful_memories()
            Planner->>WP: await WritePlan.run(context)
            WP->>LLM: await aask(prompt)
            LLM-->>WP: plan JSON
            WP-->>Planner: rsp

            Planner->>WMem: add(Message(rsp))
            Planner->>Planner: precheck_update_plan_from_rsp()

            alt Plan invalid & retries left
                Planner->>WMem: add(error_msg)
                Note over Planner: Retry generation
            else Plan valid
                Planner->>AR: await ask_review()
                AR-->>Planner: (review, confirmed)
                alt Not confirmed
                    Planner->>WMem: add(review feedback)
                    Note over Planner: Regenerate plan
                else Confirmed
                    Planner->>Plan: update_plan_from_rsp(rsp)
                    Plan->>Plan: add_tasks(tasks)<br/>topological sort
                    Planner->>WMem: clear()
                end
            end
        end
    end

    loop While planner.current_task exists
        Planner-->>Role: task
        Role->>Role: await _act_on_task(task)
        Role-->>Planner: TaskResult

        Planner->>Planner: process_task_result()
        Planner->>AR: await ask_review(task_result)
        AR-->>Planner: (review, confirmed)

        alt Confirmed
            Planner->>Plan: task.update_task_result()
            Planner->>Plan: finish_current_task()
            Plan->>Plan: task.is_finished = True<br/>advance to next task
            Planner->>WMem: clear()
        else "redo" in review
            Note over Planner: Re-execute same task
        else Other feedback
            Planner->>Planner: await update_plan()
            Note over Planner: Revise remaining tasks
        end
    end

    Planner-->>Role: completed plan as Message
    Role->>Role: memory.add(rsp)
    Role-->>Role: return rsp
```

## 9. Memory Operations During Role Lifecycle

```mermaid
sequenceDiagram
    participant Role
    participant MsgBuf as MessageQueue
    participant Mem as rc.memory
    participant WMem as rc.working_memory
    participant Idx as Memory.index

    Note over Role: === Receive Phase ===
    Role->>MsgBuf: pop_all()
    MsgBuf-->>Role: news[]

    Note over Role: === Store Phase ===
    loop For each message in news
        Role->>Mem: add(message)
        Mem->>Mem: storage.append(message)
        Mem->>Idx: index[cause_by].append(message)
    end

    Note over Role: === Recall Phase ===
    Role->>Mem: get_by_actions(rc.watch)
    Mem->>Idx: Lookup by action keys
    Idx-->>Mem: matching messages
    Mem-->>Role: important_memory[]

    Role->>Mem: get()
    Mem-->>Role: full history[]

    Note over Role: === Act Phase ===
    Role->>Role: _act() produces response msg
    Role->>Mem: add(response msg)

    Note over Role: === Working Memory (Planner) ===
    Role->>WMem: add(intermediate msg)
    Note over WMem: Discarded after<br/>each task completes
    Role->>WMem: clear()
```

## 10. End-to-End Software Company — Full Sequence

```mermaid
sequenceDiagram
    actor User
    participant Team
    participant Env as Environment
    participant PM as ProductManager
    participant Arch as Architect
    participant Eng as Engineer
    participant QA as QAEngineer
    participant LLM as BaseLLM
    participant CM as CostManager

    User->>Team: Team(context=ctx)
    User->>Team: hire([PM, Arch, Eng, QA])
    User->>Team: invest(10.0)
    User->>Team: await run(idea="Build a CLI tool")

    %% Round 0: Publish idea
    Team->>Env: publish_message(Message("Build a CLI tool"))
    Env->>PM: put_message(msg) [watches UserRequirement]

    %% Round 1: PM writes PRD
    Team->>CM: check balance
    Team->>Env: await run()

    activate PM
    PM->>PM: _observe() → news found
    PM->>PM: _think() → todo = WritePRD
    PM->>LLM: WritePRD.run(history)
    LLM-->>PM: PRD document
    PM->>PM: _act() → AIMessage(PRD)
    PM->>Env: publish_message(PRD msg)
    deactivate PM

    Env->>Arch: put_message(PRD) [watches WritePRD]

    %% Round 2: Architect writes design
    Team->>CM: check balance
    Team->>Env: await run()

    activate Arch
    Arch->>Arch: _observe() → PRD received
    Arch->>Arch: _think() → todo = WriteDesign
    Arch->>LLM: WriteDesign.run(history)
    LLM-->>Arch: System Design
    Arch->>Arch: _act() → AIMessage(Design)
    Arch->>Env: publish_message(Design msg)
    deactivate Arch

    Env->>Eng: put_message(Design) [watches WriteDesign]

    %% Round 3: Engineer writes code
    Team->>CM: check balance
    Team->>Env: await run()

    activate Eng
    Eng->>Eng: _observe() → Design received
    Eng->>Eng: _think() → todo = WriteCode
    Eng->>LLM: WriteCode.run(history)
    LLM-->>Eng: Source code
    Eng->>Eng: _act() → AIMessage(Code)
    Eng->>Env: publish_message(Code msg)
    deactivate Eng

    Env->>QA: put_message(Code) [watches WriteCode]

    %% Round 4: QA writes tests
    Team->>CM: check balance
    Team->>Env: await run()

    activate QA
    QA->>QA: _observe() → Code received
    QA->>QA: _think() → todo = WriteTest
    QA->>LLM: WriteTest.run(history)
    LLM-->>QA: Test code
    QA->>QA: _act() → AIMessage(Tests)
    QA->>Env: publish_message(Tests msg)
    deactivate QA

    %% Wrap up
    Team->>Env: is_idle? → True
    Team->>Env: archive()
    Team-->>User: return env.history
```
