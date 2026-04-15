# 6. React vs Plan-and-Act — Two Agent Strategies

## Side-by-Side Comparison

```mermaid
graph TB
    subgraph REACT ["🔄 REACT Mode"]
        direction TB
        R_Start(["Start"]) --> R_Observe["_observe()<br/>Read new messages"]
        R_Observe --> R_Think["_think()<br/>LLM selects next action"]
        R_Think --> R_HasTodo{"has_todo?"}
        R_HasTodo -- "No" --> R_Done(["Done"])
        R_HasTodo -- "Yes" --> R_Act["_act()<br/>Execute selected action"]
        R_Act --> R_Count{"actions_taken<br/>< max_react_loop?"}
        R_Count -- "Yes" --> R_Think
        R_Count -- "No" --> R_Done
        R_Done --> R_Publish["publish_message()"]
    end

    subgraph PLAN ["📋 PLAN_AND_ACT Mode"]
        direction TB
        P_Start(["Start"]) --> P_Observe["_observe()<br/>Read new messages"]
        P_Observe --> P_HasPlan{"Plan exists?"}
        P_HasPlan -- "No" --> P_Create["Planner.update_plan()<br/>LLM generates task list"]
        P_Create --> P_Review["ask_review()<br/>Human or auto confirm"]
        P_Review -- "Rejected" --> P_Create
        P_Review -- "Confirmed" --> P_Loop
        P_HasPlan -- "Yes" --> P_Loop
        P_Loop{"Next task?"}
        P_Loop -- "Yes" --> P_Act["_act_on_task(task)<br/>Execute current task"]
        P_Act --> P_Result["process_task_result()"]
        P_Result --> P_Confirm{"Confirmed?"}
        P_Confirm -- "Yes" --> P_Finish["finish_current_task()<br/>Advance to next"]
        P_Confirm -- "Redo" --> P_Act
        P_Confirm -- "Revise" --> P_Create
        P_Finish --> P_Loop
        P_Loop -- "No" --> P_Done(["Done"])
        P_Done --> P_Publish["publish_message()"]
    end

    style REACT fill:#E3F2FD,stroke:#1565C0,color:#0D47A1
    style PLAN fill:#FFF3E0,stroke:#E65100,color:#BF360C
    style R_Done fill:#E8F5E9,stroke:#2E7D32
    style P_Done fill:#E8F5E9,stroke:#2E7D32
    style R_Think fill:#FFFDE7,stroke:#F9A825
    style P_Create fill:#FFFDE7,stroke:#F9A825
```

## When to Use Which

```mermaid
graph LR
    subgraph Comparison ["⚖️ Strategy Comparison"]
        direction TB

        subgraph ReactBox ["🔄 REACT"]
            direction TB
            R1["✅ Simple, fast"]
            R2["✅ Good for single-action roles"]
            R3["✅ LLM picks action dynamically"]
            R4["⚠️ Limited lookahead"]
            R5["📌 Used by: PM, Architect, QA"]
        end

        subgraph ByOrderBox ["📑 BY_ORDER"]
            direction TB
            B1["✅ Deterministic sequence"]
            B2["✅ No LLM overhead for selection"]
            B3["✅ Predictable execution"]
            B4["⚠️ No adaptive behavior"]
            B5["📌 Used by: fixed pipelines"]
        end

        subgraph PlanBox ["📋 PLAN_AND_ACT"]
            direction TB
            P1["✅ Handles complex multi-step tasks"]
            P2["✅ Human review gates"]
            P3["✅ Can revise plan mid-execution"]
            P4["⚠️ Higher LLM cost"]
            P5["📌 Used by: DataInterpreter, RoleZero"]
        end
    end

    style Comparison fill:#FAFAFA,stroke:#9E9E9E
    style ReactBox fill:#E3F2FD,stroke:#1565C0
    style ByOrderBox fill:#F3E5F5,stroke:#6A1B9A
    style PlanBox fill:#FFF3E0,stroke:#E65100
```

> **Talking point:** The framework supports three reaction strategies. REACT is the default — a think-act loop where the LLM dynamically picks the next action each cycle. BY_ORDER runs actions in a fixed sequence with no LLM overhead. PLAN_AND_ACT is the most sophisticated — the LLM first generates a full task plan, then executes tasks one by one with review gates between each step. The plan can be revised mid-flight based on feedback. Simple roles use REACT; complex autonomous agents like DataInterpreter use PLAN_AND_ACT.
