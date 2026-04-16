# 3. Role Internals — Anatomy of an Agent

```mermaid
graph TB
    subgraph Role ["🤖 Role (Agent)"]
        direction TB

        subgraph Identity ["Identity"]
            Name["name / profile"]
            Goal["goal"]
            Constraints["constraints"]
        end

        subgraph RC ["RoleContext — Runtime State"]
            direction TB
            MsgBuf["📬 msg_buffer<br/><i>MessageQueue</i><br/>Incoming messages"]
            Mem["🧠 memory<br/><i>Memory</i><br/>All observed messages"]
            WMem["📝 working_memory<br/><i>Memory</i><br/>Current task scratch"]
            Watch["👀 watch set<br/><i>Action types to listen for</i>"]
            State["🔢 state<br/><i>Current action index</i>"]
            Todo["⚡ todo<br/><i>Next Action to execute</i>"]
            Mode["🔄 react_mode<br/><i>REACT | BY_ORDER | PLAN_AND_ACT</i>"]
        end

        subgraph Actions ["Action List"]
            A1["Action 1"]
            A2["Action 2"]
            A3["Action N"]
        end

        subgraph Loop ["♻️ Observe → Think → Act"]
            Observe["_observe()<br/>Pop msg_buffer<br/>Filter by watch<br/>Store in memory"]
            Think["_think()<br/>Select next action<br/>Set state & todo"]
            Act["_act()<br/>Execute todo.run()<br/>Wrap response as Message<br/>Store in memory"]
            Publish["publish_message()<br/>Send result to Environment"]
        end
    end

    MsgBuf --> Observe
    Watch --> Observe
    Observe --> Mem
    Observe --> Think
    Mem --> Think
    State --> Think
    Think --> Todo
    Todo --> Act
    Actions --> Todo
    Act --> Mem
    Act --> Publish

    Env((📡 Environment)) -- "put_message()" --> MsgBuf
    Publish -- "env.publish_message()" --> Env

    style Role fill:#F3E5F5,stroke:#6A1B9A,color:#4A148C
    style RC fill:#EDE7F6,stroke:#7E57C2
    style Identity fill:#E8EAF6,stroke:#3F51B5
    style Actions fill:#FFFDE7,stroke:#F9A825
    style Loop fill:#E8F5E9,stroke:#2E7D32
    style Env fill:#FFF3E0,stroke:#E65100
```

> **Talking point:** Each Role is a self-contained agent. It has an identity (name, goal, constraints), a runtime context (message buffer, memory, watch set), and a list of Actions it can perform. The core loop is simple: observe new messages → think about what to do → act on it → publish the result back to the Environment.
