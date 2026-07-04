# Mermaid 图表指南

本文件提供教学文档中常用的 Mermaid 图表类型、写法示例和使用场景。
Mermaid 语法被语雀、飞书、Notion、GitHub、Typora 等主流云笔记和 Markdown 编辑器原生支持。

---

## 目录

1. [流程图 Flowchart](#流程图-flowchart)
2. [时序图 Sequence Diagram](#时序图-sequence-diagram)
3. [状态图 State Diagram](#状态图-state-diagram)
4. [类图 Class Diagram](#类图-class-diagram)
5. [ER 图 Entity Relationship Diagram](#er-图-entity-relationship-diagram)
6. [甘特图 Gantt](#甘特图-gantt)
7. [使用场景速查表](#使用场景速查表)
8. [写作技巧](#写作技巧)

---

## 流程图 Flowchart

最常用的图表类型。适合展示算法步骤、决策流程、系统架构。

### 基本语法

```mermaid
flowchart TD
    A[开始] --> B{条件判断}
    B -->|是| C[执行操作 A]
    B -->|否| D[执行操作 B]
    C --> E[结束]
    D --> E
```

### 节点形状

```mermaid
flowchart LR
    A[矩形 - 普通步骤]
    B{菱形 - 判断条件}
    C([圆角矩形 - 开始/结束])
    D[/平行四边形 - 输入/输出/]
    E[(圆柱 - 数据存储)]
    F>旗帜 - 注释/说明]
```

### 示例：二分查找流程

```mermaid
flowchart TD
    Start([开始]) --> Init["left=0, right=n-1"]
    Init --> Loop{left <= right?}
    Loop -->|否| NotFound["返回 -1（未找到）"]
    Loop -->|是| Calc["mid = (left + right) / 2"]
    Calc --> Compare{arr[mid] vs target}
    Compare -->|arr[mid] == target| Found["返回 mid"]
    Compare -->|arr[mid] < target| MoveLeft["left = mid + 1"]
    Compare -->|arr[mid] > target| MoveRight["right = mid - 1"]
    MoveLeft --> Loop
    MoveRight --> Loop
    Found --> End([结束])
    NotFound --> End
```

### 示例：模拟数据结构

用 flowchart 可以模拟树形结构：

```mermaid
flowchart TD
    Root((50)) --> L30((30))
    Root --> R70((70))
    L30 --> L20((20))
    L30 --> L40((40))
    R70 --> R60((60))
    R70 --> R80((80))
```

链表结构：

```mermaid
flowchart LR
    Head[Head] --> N1["Node(10)"]
    N1 --> N2["Node(20)"]
    N2 --> N3["Node(30)"]
    N3 --> Null[NULL]
```

---

## 时序图 Sequence Diagram

适合展示组件间交互、网络协议通信、函数调用链。

### 基本语法

```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as 服务器
    C->>S: 发送请求 (SYN)
    S-->>C: 确认请求 (SYN-ACK)
    C->>S: 确认连接 (ACK)
    Note over C,S: 连接建立
    C->>S: 发送数据
    S-->>C: 返回响应
```

### 示例：TCP 三次握手

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant Server as 服务器

    Note over Client: 初始状态: CLOSED
    Note over Server: 初始状态: LISTEN

    Client->>Server: SYN (seq=x)
    Note over Client: 进入 SYN_SENT

    Server->>Client: SYN+ACK (seq=y, ack=x+1)
    Note over Server: 进入 SYN_RCVD

    Client->>Server: ACK (ack=y+1)
    Note over Client: 进入 ESTABLISHED
    Note over Server: 进入 ESTABLISHED

    Note over Client,Server: 连接建立，可以传输数据
```

### 示例：HTTP 请求生命周期

```mermaid
sequenceDiagram
    participant B as 浏览器
    participant D as DNS 服务器
    participant W as Web 服务器

    B->>D: 查询 example.com 的 IP
    D-->>B: 返回 93.184.216.34

    B->>W: HTTP GET /index.html
    Note over B,W: TCP 连接已建立

    W->>W: 路由匹配 + 查询数据库
    W-->>B: 200 OK + HTML 内容

    B->>B: 解析 HTML，渲染页面
```

### 高级用法

```mermaid
sequenceDiagram
    participant A as 前端
    participant B as API 网关
    participant C as 用户服务
    participant D as 数据库

    A->>+B: POST /api/login
    B->>+C: validateUser(email, pwd)
    C->>+D: SELECT * FROM users WHERE email=?
    D-->>-C: 用户记录
    C-->>-B: { valid: true, token: "xxx" }

    alt 验证成功
        B-->>A: 200 { token }
    else 验证失败
        B-->>A: 401 { error: "密码错误" }
    end
```

---

## 状态图 State Diagram

适合展示对象状态转换、协议状态机、生命周期。

### 基本语法

```mermaid
stateDiagram-v2
    [*] --> 空闲
    空闲 --> 运行中: 启动
    运行中 --> 暂停: 暂停
    暂停 --> 运行中: 恢复
    运行中 --> 空闲: 停止
    暂停 --> 空闲: 停止
    空闲 --> [*]
```

### 示例：进程状态转换

```mermaid
stateDiagram-v2
    [*] --> 就绪: 创建进程
    就绪 --> 运行: 调度器选中
    运行 --> 就绪: 时间片用完
    运行 --> 阻塞: 等待 I/O
    阻塞 --> 就绪: I/O 完成
    运行 --> [*]: 进程结束
```

### 示例：HTTP 请求状态

```mermaid
stateDiagram-v2
    [*] --> 未发送
    未发送 --> 发送中: 调用 send()
    发送中 --> 等待响应: 请求已发出
    等待响应 --> 成功: 收到 2xx
    等待响应 --> 重定向: 收到 3xx
    等待响应 --> 客户端错误: 收到 4xx
    等待响应 --> 服务器错误: 收到 5xx
    等待响应 --> 超时: 超过时限
    重定向 --> 发送中: 跟随新地址
    成功 --> [*]
    客户端错误 --> [*]
    服务器错误 --> [*]
    超时 --> [*]
```

---

## 类图 Class Diagram

适合展示面向对象设计、类继承关系、设计模式结构。

### 基本语法

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +void eat()
        +void sleep()
    }

    class Dog {
        +void bark()
    }

    class Cat {
        +void meow()
    }

    Animal <|-- Dog
    Animal <|-- Cat
```

### 示例：设计模式——观察者模式

```mermaid
classDiagram
    class Subject {
        +List~Observer~ observers
        +attach(observer)
        +detach(observer)
        +notify()
    }

    class ConcreteSubject {
        +String state
        +getState()
        +setState(state)
    }

    class Observer {
        <<interface>>
        +update()
    }

    class ConcreteObserver {
        +update()
    }

    Subject <|-- ConcreteSubject
    Observer <|.. ConcreteObserver
    Subject o-- Observer : observes
```

### 关系类型说明

```mermaid
classDiagram
    classA <|-- classB : 继承(实线空心三角)
    classC <|.. classD : 实现(虚线空心三角)
    classE --> classF : 关联(实线箭头)
    classG o-- classH : 聚合(实线空心菱形)
    classI *-- classJ : 组合(实线实心菱形)
```

---

## ER 图 Entity Relationship Diagram

适合展示数据库表结构、实体关系。

### 基本语法

```mermaid
erDiagram
    STUDENT ||--o{ ENROLLMENT : "注册"
    COURSE ||--o{ ENROLLMENT : "被注册"

    STUDENT {
        int id PK
        string name
        string email
    }

    COURSE {
        int id PK
        string title
        int credits
    }

    ENROLLMENT {
        int student_id FK
        int course_id FK
        date enroll_date
    }
```

### 关系基数

```mermaid
erDiagram
    A ||--|| B : "一对一"
    A ||--o{ C : "一对多(可空)"
    A }o--o{ D : "多对多"
    A }o--|| E : "多对一(必须)"
```

---

## 甘特图 Gantt

适合展示项目计划、开发周期、课程进度安排。

```mermaid
gantt
    title 软件工程项目进度
    dateFormat YYYY-MM-DD
    section 需求阶段
    需求分析     :a1, 2025-03-01, 7d
    需求评审     :after a1, 3d
    section 设计阶段
    系统设计     :a2, after a1, 10d
    设计评审     :after a2, 2d
    section 开发阶段
    编码实现     :a3, after a2, 20d
    单元测试     :after a3, 7d
    section 上线阶段
    集成测试     :after a3, 5d
    部署上线     :after a3, 3d
```

---

## 使用场景速查表

| 知识点类型 | 推荐图表 | 说明 |
|-----------|---------|------|
| 排序/查找算法 | flowchart | 展示算法步骤和分支判断 |
| 树/图/链表结构 | flowchart | 模拟数据结构的节点和指针 |
| TCP/HTTP 等协议 | sequenceDiagram | 展示通信时序和消息交互 |
| 函数调用链 | sequenceDiagram | 展示模块间调用关系 |
| 进程/线程状态 | stateDiagram | 展示状态转换和触发条件 |
| 对象生命周期 | stateDiagram | 展示对象从创建到销毁 |
| 面向对象设计 | classDiagram | 展示类继承、接口实现、关联关系 |
| 设计模式 | classDiagram | 展示模式中各角色及其关系 |
| 数据库设计 | erDiagram | 展示表结构和外键关系 |
| 项目管理/课程计划 | gantt | 展示时间线和任务依赖 |

---

## 写作技巧

### 1. 图表要有标题和说明

在 Mermaid 代码块前面用一句话说明"这张图展示了什么"，后面用一段话解读图中关键信息。

```markdown
下面的流程图展示了快速排序的一次完整执行过程：

​```mermaid
flowchart TD
    ...
​```

注意图中分区操作的三个关键步骤：选基准、遍历比较、交换位置。这就是一次完整的 partition。
```

### 2. 图表不要太复杂

如果一张图超过 15 个节点，考虑拆成多张图。学生的认知负荷有限，一张图讲清楚一个要点即可。

### 3. 用注释补充上下文

Mermaid 支持在图中添加 Note，善用它来标注关键信息：

```mermaid
sequenceDiagram
    participant A as 客户端
    participant B as 服务器
    A->>B: 请求
    Note over B: 这里服务器处理了 200ms
    B-->>A: 响应
```

### 4. 中文节点名

Mermaid 完全支持中文节点名，但注意用引号包裹包含特殊字符的文本：

```mermaid
flowchart TD
    A[开始排序] --> B{数组为空?}
    B -->|是| C[返回空数组]
    B -->|否| D[选择基准元素]
```

### 5. 颜色提示

可以用 `style` 给关键节点加颜色，突出重点：

```mermaid
flowchart TD
    A[开始] --> B[处理数据]
    B --> C{是否出错?}
    C -->|否| D[返回结果]
    C -->|是| E[抛出异常]

    style E fill:#f96,stroke:#333,stroke-width:2px
    style D fill:#9f9,stroke:#333,stroke-width:2px
```
