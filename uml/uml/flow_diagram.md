# Flow UML Diagram — SdeTeam (MetaGPT)

## 1. Main Execution Flow

```mermaid
flowchart TD
    Start([User / CLI]) -->|"idea + roles"| Init["Team.__init__()"]
    Init --> CreateCtx["Create Context"]
    CreateCtx --> CreateEnv{"use_mgx?"}
    CreateEnv -->|Yes| MGX["env = MGXEnv(ctx)"]
    CreateEnv -->|No| Env["env = Environment(ctx)"]
    MGX --> Hire
    Env --> Hire
    Hire["team.hire(roles)"] --> AddRoles["env.add_roles(roles)\nSet context & env on each Role"]
    AddRoles --> Invest["team.invest(investment)\nSet max_budget"]
    Invest --> RunProject["team.run_project(idea)\nPublish initial Message to env"]
    RunProject --> RunLoop

    subgraph RunLoop ["team.run() — Main Loop"]
        CheckIdle{"env.is_idle?"}
        CheckIdle -->|Yes| EndLoop([All roles idle — stop])
        CheckIdle -->|No| CheckBudget{"Budget exceeded?"}
        CheckBudget -->|Yes| NoMoney([NoMoneyException])
        CheckBudget -->|No| EnvRun["await env.run()"]
        EnvRun --> Decrement["n_round -= 1"]
        Decrement --> CheckRound{"n_round > 0?"}
        CheckRound -->|Yes| CheckIdle
        CheckRound -->|No| EndLoop
    end

    EndLoop --> Archive["env.archive()"]
    Archive --> ReturnHistory(["Return env.history"])
```

## 2. Environment Run — Parallel Role Execution

```mermaid
flowchart TD
    EnvRun(["env.run()"]) --> IterRoles["Iterate over env.roles"]
    IterRoles --> CheckRoleIdle{"role.is_idle?"}
    CheckRoleIdle -->|Yes| SkipRole["Skip role"]
    CheckRoleIdle -->|No| AddFuture["Add role.run() to futures"]
    SkipRole --> NextRole{"More roles?"}
    AddFuture --> NextRole
    NextRole -->|Yes| CheckRoleIdle
    NextRole -->|No| GatherCheck{"futures not empty?"}
    GatherCheck -->|Yes| Gather["await asyncio.gather(*futures)"]
    GatherCheck -->|No| Done
    Gather --> Done(["Round complete"])
```

## 3. Role Execution Lifecycle — role.run()

```mermaid
flowchart TD
    RoleRun(["role.run(with_message)"]) --> HasMsg{"with_message\nprovided?"}
    HasMsg -->|Yes| WrapMsg["Wrap as Message\nSet cause_by = UserRequirement"]
    WrapMsg --> PutMsg["role.put_message(msg)\nPush to rc.msg_buffer"]
    PutMsg --> Observe
    HasMsg -->|No| Observe

    Observe["await _observe()"] --> ReadBuffer["Pop all from rc.msg_buffer"]
    ReadBuffer --> FilterNews["Filter messages:\ncause_by in rc.watch\nOR name in send_to"]
    FilterNews --> StoreMemory["Add news to rc.memory"]
    StoreMemory --> HasNews{"len(news) > 0?"}
    HasNews -->|No| Idle(["No news — suspend"])
    HasNews -->|Yes| React["await react()"]

    React --> ReactMode{"rc.react_mode?"}

    ReactMode -->|REACT / BY_ORDER| ReactLoop
    ReactMode -->|PLAN_AND_ACT| PlanAct

    subgraph ReactLoop ["_react() — Think-Act Loop"]
        direction TB
        Think["await _think()"] --> HasTodo{"has_todo?"}
        HasTodo -->|No| ExitLoop(["Break — no action needed"])
        HasTodo -->|Yes| Act["await _act()"]
        Act --> IncCount["actions_taken += 1"]
        IncCount --> MaxLoop{"actions_taken\n< max_react_loop?"}
        MaxLoop -->|Yes| Think
        MaxLoop -->|No| ExitLoop
    end

    subgraph PlanAct ["_plan_and_act()"]
        direction TB
        HasPlan{"plan.goal\nexists?"} -->|No| CreatePlan["planner.update_plan(goal)"]
        HasPlan -->|Yes| TaskLoop
        CreatePlan --> TaskLoop
        TaskLoop{"planner.current_task\nexists?"} -->|Yes| ActOnTask["await _act_on_task(task)"]
        ActOnTask --> ProcessResult["planner.process_task_result()"]
        ProcessResult --> TaskLoop
        TaskLoop -->|No| ReturnPlan(["Return completed plan"])
    end

    ReactLoop --> ResetState
    PlanAct --> ResetState
    ResetState["set_todo(None)\nReset state to -1"]
    ResetState --> Publish["publish_message(rsp)"]
    Publish --> ReturnRsp(["Return response Message"])
```

## 4. Role._think() — Action Selection

```mermaid
flowchart TD
    Think(["_think()"]) --> SingleAction{"Only 1 action?"}
    SingleAction -->|Yes| SetState0["set_state(0)"] --> RetTrue(["return True"])

    SingleAction -->|No| Recovered{"Recovered from\nserialization?"}
    Recovered -->|Yes| RestoreState["set_state(rc.state)"] --> RetTrue

    Recovered -->|No| CheckMode{"react_mode?"}

    CheckMode -->|BY_ORDER| NextState["state += 1"]
    NextState --> ValidState{"0 ≤ state\n< len(actions)?"}
    ValidState -->|Yes| RetTrue
    ValidState -->|No| RetFalse(["return False"])

    CheckMode -->|REACT| BuildPrompt["Build prompt with\nhistory + states"]
    BuildPrompt --> AskLLM["await llm.aask(prompt)"]
    AskLLM --> ParseState["Extract next_state\nfrom LLM response"]
    ParseState --> ValidLLM{"Valid state\nnumber?"}
    ValidLLM -->|No / -1| SetMinus1["state = -1"] --> RetTrue2(["return True\n(todo = None → stops)"])
    ValidLLM -->|Yes| SetN["set_state(next_state)"] --> RetTrue
```

## 5. Role._act() — Action Execution

```mermaid
flowchart TD
    Act(["_act()"]) --> RunAction["response = await rc.todo.run(rc.history)"]

    RunAction --> CheckType{"response type?"}

    CheckType -->|ActionOutput / ActionNode| WrapAI["msg = AIMessage(\n  content, instruct_content,\n  cause_by=todo, sent_from=self)"]
    CheckType -->|Message| UseMsg["msg = response"]
    CheckType -->|str / other| WrapStr["msg = AIMessage(\n  content=response,\n  cause_by=todo, sent_from=self)"]

    WrapAI --> AddMem["rc.memory.add(msg)"]
    UseMsg --> AddMem
    WrapStr --> AddMem

    AddMem --> ReturnMsg(["Return msg"])
```

## 6. Message Routing — publish_message

```mermaid
flowchart TD
    Publish(["role.publish_message(msg)"]) --> CheckNull{"msg is None?"}
    CheckNull -->|Yes| Abort(["Return — nothing to send"])
    CheckNull -->|No| FixRouting["Resolve ROUTE_TO_SELF\nSet sent_from"]

    FixRouting --> SelfOnly{"All recipients\n= self?"}
    SelfOnly -->|Yes| SelfPut["put_message(msg)\nto own msg_buffer"]
    SelfOnly -->|No| HasEnv{"rc.env exists?"}
    HasEnv -->|No| Drop(["No env — drop message"])
    HasEnv -->|Yes| EnvPublish["env.publish_message(msg)"]

    EnvPublish --> IterMembers["For each (role, addrs)\nin member_addrs"]
    IterMembers --> MatchRoute{"is_send_to(\nmsg, addrs)?"}
    MatchRoute -->|Yes| Deliver["role.put_message(msg)"]
    MatchRoute -->|No| Skip["Skip"]
    Deliver --> NextMember{"More members?"}
    Skip --> NextMember
    NextMember -->|Yes| IterMembers
    NextMember -->|No| AddHistory["env.history.add(msg)"]
    AddHistory --> Done(["Message delivered"])
```

## 7. Action.run() — LLM Interaction

```mermaid
flowchart TD
    ActionRun(["action.run(*args)"]) --> HasNode{"action.node\nexists?"}
    HasNode -->|Yes| NodePath
    HasNode -->|No| SubclassRun["Subclass-specific\nrun() implementation"]

    subgraph NodePath ["_run_action_node()"]
        BuildCtx["Build context from\nhistory messages"] --> NodeFill["await node.fill(\n  req=context, llm=self.llm)"]
        NodeFill --> Compile["node.compile()\nBuild prompt from schema"]
        Compile --> LLMCall["await llm.aask(prompt)"]
        LLMCall --> Parse["Parse LLM response\ninto structured output"]
        Parse --> ReturnNode(["Return ActionNode\nwith instruct_content"])
    end

    SubclassRun --> AskLLM["await self._aask(prompt)\n→ llm.aask(prompt, system_msgs)"]
    AskLLM --> ReturnResult(["Return result"])
```

## 8. Planner Task Lifecycle

```mermaid
flowchart TD
    UpdatePlan(["planner.update_plan(goal)"]) --> GenPlan["await WritePlan.run(context)"]
    GenPlan --> Precheck{"Plan valid?"}
    Precheck -->|No| Retry{"retries left?"}
    Retry -->|Yes| GenPlan
    Retry -->|No| AskReview
    Precheck -->|Yes| AskReview["await ask_review()"]
    AskReview --> Confirmed{"Confirmed?"}
    Confirmed -->|No| GenPlan
    Confirmed -->|Yes| ApplyPlan["update_plan_from_rsp()\nPopulate plan.tasks"]

    ApplyPlan --> TaskExec

    subgraph TaskExec ["Task Execution Loop"]
        direction TB
        GetTask{"current_task\nexists?"} -->|No| PlanDone(["Plan finished"])
        GetTask -->|Yes| Execute["await _act_on_task(task)"]
        Execute --> ProcessResult["planner.process_task_result()"]
        ProcessResult --> ReviewResult["await ask_review(task_result)"]
        ReviewResult --> ResultConfirmed{"Confirmed?"}
        ResultConfirmed -->|Yes| ConfirmTask["confirm_task()\ntask.is_finished = True\nAdvance to next task"]
        ResultConfirmed -->|"'redo'"| Execute
        ResultConfirmed -->|Other| ReplanTask["update_plan()\nRevise remaining tasks"]
        ConfirmTask --> GetTask
        ReplanTask --> GetTask
    end
```

## 9. End-to-End Sequence (Software Company Example)

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

    User->>Team: run(idea="Build a CLI tool")
    Team->>Env: publish_message(Message(idea))
    Note over Env: Message routed to PM<br/>(watches UserRequirement)

    Env->>PM: put_message(msg)
    PM->>PM: _observe() → news found
    PM->>PM: react() → _think() → _act()
    PM->>LLM: WritePRD.run()
    LLM-->>PM: PRD content
    PM->>Env: publish_message(PRD)
    Note over Env: Routed to Architect<br/>(watches WritePRD)

    Env->>Arch: put_message(PRD)
    Arch->>Arch: _observe() → _think() → _act()
    Arch->>LLM: WriteDesign.run()
    LLM-->>Arch: System Design
    Arch->>Env: publish_message(Design)
    Note over Env: Routed to Engineer<br/>(watches WriteDesign)

    Env->>Eng: put_message(Design)
    Eng->>Eng: _observe() → _think() → _act()
    Eng->>LLM: WriteCode.run()
    LLM-->>Eng: Source Code
    Eng->>Env: publish_message(Code)
    Note over Env: Routed to QA<br/>(watches WriteCode)

    Env->>QA: put_message(Code)
    QA->>QA: _observe() → _think() → _act()
    QA->>LLM: WriteTest.run()
    LLM-->>QA: Test Code
    QA->>Env: publish_message(Tests)

    Note over Env: All roles idle → loop ends
    Env-->>Team: history
    Team->>Team: archive()
    Team-->>User: Return history
```
