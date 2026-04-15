# 1. System Overview — Layered Architecture

```mermaid
block-beta
    columns 1

    block:USER["🧑‍💻 USER / CLI"]
        style USER fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20
        U1["run(idea, n_round)"]
        U2["invest(budget)"]
        U3["hire(roles)"]
    end

    block:ORCH["🎯 ORCHESTRATION LAYER"]
        style ORCH fill:#E3F2FD,stroke:#1565C0,color:#0D47A1
        T1["Team"]
        T2["Context"]
        T3["Config"]
        T4["CostManager"]
    end

    block:ENV["📡 ENVIRONMENT LAYER  (Message Bus)"]
        style ENV fill:#FFF3E0,stroke:#E65100,color:#BF360C
        E1["Environment / MGXEnv"]
        E2["Message Routing"]
        E3["History Memory"]
        E4["Address Registry"]
    end

    block:AGENT["🤖 AGENT LAYER  (Roles)"]
        style AGENT fill:#F3E5F5,stroke:#6A1B9A,color:#4A148C
        A1["ProductManager"]
        A2["Architect"]
        A3["Engineer"]
        A4["QAEngineer"]
        A5["RoleZero"]
        A6["DataInterpreter"]
    end

    block:ACTION["⚡ ACTION LAYER"]
        style ACTION fill:#FFFDE7,stroke:#F9A825,color:#F57F17
        AC1["WritePRD"]
        AC2["WriteDesign"]
        AC3["WriteCode"]
        AC4["WriteTest"]
        AC5["ActionNode"]
    end

    block:LLM["🧠 LLM PROVIDER LAYER"]
        style LLM fill:#FCE4EC,stroke:#C62828,color:#B71C1C
        L1["OpenAI"]
        L2["Anthropic"]
        L3["Azure"]
        L4["Gemini"]
        L5["Bedrock"]
        L6["Ollama"]
    end

    block:DATA["💾 DATA LAYER"]
        style DATA fill:#E0F2F1,stroke:#00695C,color:#004D40
        D1["Memory"]
        D2["Message / MessageQueue"]
        D3["Plan / Task"]
        D4["Document"]
    end

    USER --> ORCH
    ORCH --> ENV
    ENV --> AGENT
    AGENT --> ACTION
    ACTION --> LLM
    AGENT --> DATA
```

> **Talking point:** The system is organized in clean layers. The User interacts only with the Team. The Team orchestrates Roles through an Environment that acts as a message bus. Each Role executes Actions that call LLM providers, with all state managed in the Data layer.
