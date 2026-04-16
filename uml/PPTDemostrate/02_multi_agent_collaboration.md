# 2. Multi-Agent Collaboration — SOP-Driven Pipeline

```mermaid
graph LR
    User((👤 User))

    subgraph Environment ["📡 Environment — Central Message Bus"]
        direction TB
        Router["Message Router<br/>Address Matching"]
        History["History Memory"]
    end

    subgraph Agents ["🤖 Agent Team"]
        direction TB
        PM["🗂️ ProductManager<br/><i>watches: UserRequirement</i>"]
        Arch["📐 Architect<br/><i>watches: WritePRD</i>"]
        Eng["💻 Engineer<br/><i>watches: WriteDesign</i>"]
        QA["🧪 QAEngineer<br/><i>watches: WriteCode</i>"]
    end

    User -- "idea" --> Router

    Router -- "UserRequirement" --> PM
    PM -- "PRD ✅" --> Router
    Router -- "WritePRD" --> Arch
    Arch -- "Design ✅" --> Router
    Router -- "WriteDesign" --> Eng
    Eng -- "Code ✅" --> Router
    Router -- "WriteCode" --> QA
    QA -- "Tests ✅" --> Router

    Router -. "log all" .-> History

    style Environment fill:#FFF3E0,stroke:#E65100,color:#BF360C
    style Agents fill:#F3E5F5,stroke:#6A1B9A,color:#4A148C
    style Router fill:#FFE0B2,stroke:#EF6C00
    style History fill:#FFE0B2,stroke:#EF6C00
    style PM fill:#E8F5E9,stroke:#2E7D32
    style Arch fill:#E3F2FD,stroke:#1565C0
    style Eng fill:#FFFDE7,stroke:#F9A825
    style QA fill:#FCE4EC,stroke:#C62828
```

> **Talking point:** Agents don't talk to each other directly. Every message flows through the Environment, which routes it based on what each Role "watches." This creates a clean SOP pipeline: User → PM → Architect → Engineer → QA, with each agent triggered automatically when its upstream dependency publishes a result.
