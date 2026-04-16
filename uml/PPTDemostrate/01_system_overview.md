# 1. System Overview — Layered Architecture

```mermaid
graph TB
    subgraph USER ["🧑‍💻 User / CLI"]
        direction LR
        U1(["run(idea, n_round)"])
        U2(["invest(budget)"])
        U3(["hire(roles)"])
    end

    subgraph ORCH ["🎯 Orchestration"]
        direction LR
        T["Team"]
        CTX["Context"]
        CFG["Config"]
        COST["CostManager"]
        T --- CTX --- CFG --- COST
    end

    subgraph ENV ["📡 Environment — Message Bus"]
        direction LR
        E["Environment<br/>MGXEnv"]
        MR["Message<br/>Routing"]
        HM["History<br/>Memory"]
        AR["Address<br/>Registry"]
        E --- MR --- HM --- AR
    end

    subgraph AGENT ["🤖 Roles (Agents)"]
        direction LR
        PM["ProductManager"]
        ARCH["Architect"]
        ENG["Engineer"]
        QA["QAEngineer"]
        RZ["RoleZero"]
        DI["DataInterpreter"]
    end

    subgraph ACTION ["⚡ Actions"]
        direction LR
        WP["WritePRD"]
        WD["WriteDesign"]
        WC["WriteCode"]
        WT["WriteTest"]
        AN["ActionNode"]
    end

    subgraph LLM ["🧠 LLM Providers"]
        direction LR
        OAI["OpenAI"]
        ANT["Anthropic"]
        AZ["Azure"]
        GEM["Gemini"]
        BED["Bedrock"]
        OLL["Ollama"]
    end

    subgraph DATA ["💾 Data"]
        direction LR
        MEM["Memory"]
        MSG["Message<br/>MessageQueue"]
        PLN["Plan / Task"]
        DOC["Document"]
    end

    USER ==> ORCH
    ORCH ==> ENV
    ENV ==> AGENT
    AGENT ==> ACTION
    ACTION ==> LLM
    AGENT -.-> DATA
    ENV -.-> DATA

    style USER fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20,stroke-width:2px
    style ORCH fill:#E3F2FD,stroke:#1565C0,color:#0D47A1,stroke-width:2px
    style ENV fill:#FFF3E0,stroke:#E65100,color:#BF360C,stroke-width:2px
    style AGENT fill:#F3E5F5,stroke:#6A1B9A,color:#4A148C,stroke-width:2px
    style ACTION fill:#FFFDE7,stroke:#F9A825,color:#F57F17,stroke-width:2px
    style LLM fill:#FCE4EC,stroke:#C62828,color:#B71C1C,stroke-width:2px
    style DATA fill:#E0F2F1,stroke:#00695C,color:#004D40,stroke-width:2px
```

> **Talking point:** 7 层自顶向下：User 只接触 Team → Team 通过 Environment（消息总线）调度 Roles → 每个 Role 执行 Action 调用 LLM → 所有状态存储在 Data 层。实线 `==>` 表示调用链，虚线 `-.->` 表示数据读写。
