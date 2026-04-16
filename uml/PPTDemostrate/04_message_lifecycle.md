# 4. Message Lifecycle — Pub/Sub Routing

```mermaid
graph LR
    subgraph Origin ["1️⃣ Origin"]
        Sender["🤖 Sender Role<br/>publish_message(msg)"]
    end

    subgraph Routing ["2️⃣ Environment Routing"]
        direction TB
        Resolve["Resolve routing<br/>• Set sent_from<br/>• Handle ROUTE_TO_SELF"]
        Match["Address matching<br/>for each (role, addrs)<br/>in member_addrs"]
        Log["Log to<br/>env.history"]
    end

    subgraph Delivery ["3️⃣ Delivery"]
        direction TB
        BufA["📬 Role A<br/>msg_buffer.push()"]
        BufB["📬 Role B<br/>msg_buffer.push()"]
        BufX["❌ Role C<br/><i>no match — skip</i>"]
    end

    subgraph Processing ["4️⃣ Processing"]
        direction TB
        Pop["msg_buffer.pop_all()"]
        Filter["Filter by<br/>watch set"]
        Store["memory.add()<br/>+ index by cause_by"]
        React["Trigger<br/>react()"]
    end

    Sender --> Resolve
    Resolve --> Match
    Match --> Log
    Match -- "✅ send_to ∩ addrs" --> BufA
    Match -- "✅ send_to ∩ addrs" --> BufB
    Match -- "❌ no overlap" --> BufX
    BufA --> Pop
    Pop --> Filter
    Filter --> Store
    Store --> React

    style Origin fill:#E8F5E9,stroke:#2E7D32
    style Routing fill:#FFF3E0,stroke:#E65100
    style Delivery fill:#E3F2FD,stroke:#1565C0
    style Processing fill:#F3E5F5,stroke:#6A1B9A
    style BufX fill:#FFEBEE,stroke:#C62828,stroke-dasharray: 5 5
```

### Message Structure

```mermaid
graph LR
    subgraph Message ["📨 Message"]
        direction TB
        ID["id: uuid"]
        Content["content: str"]
        MRole["role: user | assistant | system"]
        CauseBy["cause_by: Action class name"]
        SentFrom["sent_from: sender Role"]
        SendTo["send_to: set of recipients"]
        Meta["metadata: dict"]
    end

    CauseBy -. "matched against" .-> Watch["👀 Role.watch set"]
    SendTo -. "matched against" .-> Addrs["📋 Environment.member_addrs"]

    style Message fill:#FFFDE7,stroke:#F9A825
    style Watch fill:#F3E5F5,stroke:#6A1B9A
    style Addrs fill:#FFF3E0,stroke:#E65100
```

> **Talking point:** Messages are the only way agents communicate. A sender publishes a Message to the Environment, which checks each registered Role's address set. Matching roles receive the message in their private buffer. During `_observe()`, the role filters messages by its watch set (the Action types it cares about), stores them in memory, and triggers the react cycle. It's a clean pub/sub pattern with content-based routing.
