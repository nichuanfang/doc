# Flowable 知识点

## 1. 相关表（数据库表）

表名以 ACT_ 开头（部分扩展为 `FLW_`），按用途分类：

| 前缀    | 含义                     | 核心表示例                                                                                                    | 说明                                                                                  |
| ------- | ------------------------ | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| ACT_RE_ | Repository（仓库，静态） | ACT_RE_DEPLOYMENT`、`ACT_RE_PROCDEF`、`ACT_RE_MODEL                                                           | 部署记录、流程定义元数据、模型                                                        |
| ACT_RU_ | Runtime（运行时）        | ACT_RU_EXECUTION`、`ACT_RU_TASK`、`ACT_RU_VARIABLE`、`ACT_RU_JOB`、`ACT_RU_IDENTITYLINK                       | 流程实例/执行、待办任务、变量、异步作业、候选人。**流程结束后自动删除**，保持表小而快 |
| ACT_HI_ | History（历史）          | ACT_HI_PROCINST`、`ACT_HI_TASKINST`、`ACT_HI_ACTINST`、`ACT_HI_VARINST`、`ACT_HI_COMMENT`、`ACT_HI_ATTACHMENT | 历史流程实例、任务、活动节点、变量、评论、附件。**永久保留**                          |
| ACT_GE_ | General（通用）          | ACT_GE_BYTEARRAY`、`ACT_GE_PROPERTY                                                                           | 二进制资源（BPMN XML、图片、大变量）、引擎属性                                        |
| ACT_ID_ | Identity（身份）         | ACT_ID_USER`、`ACT_ID_GROUP`、`ACT_ID_MEMBERSHIP                                                              | 用户、组（生产通常禁用，对接自有权限）                                                |
| 其他    | CMMN / DMN / Event 等    | ACT_CMMN_*`、`ACT_DMN_*`、`FLW_EVENT_* 等                                                                     | 案例、决策、事件注册表                                                                |

完整初始化约 70–90 张表（含多引擎）。生产常用核心是 RE / RU / HI / GE 这几类。

## 2. 相关 Service（核心 API）

从 ProcessEngine 获取，线程安全：

- **RepositoryService**：部署、查询/删除流程定义、读取资源、版本管理
- **RuntimeService**：启动流程实例、设置/查询变量、挂起/激活、信号/消息触发、删除实例
- **TaskService**：查询待办/已办、认领、完成、转办、委托、加签、候选人
- **HistoryService**：查询历史流程、任务、活动、变量（审计、统计）
- **ManagementService**：作业管理、异步执行器、引擎信息、死信任务处理
- **IdentityService**：用户/组（生产常关闭 `idm-enabled=false`）
- **FormService**（部分版本）：表单相关
- **DynamicBpmnService**：运行时动态修改流程定义部分属性

Spring Boot 中直接 @Autowired 注入即可。

## 3. 相关流程节点（BPMN 元素）

主要 Flow Objects：

- **事件（Events）**：
  - 开始：空开始、定时、消息、信号
  - 结束：普通结束、终止结束
  - 中间/边界：定时器、消息、信号、错误、补偿等
- **活动（Activities）**：
  - User Task（用户任务）
  - Service Task（服务任务，JavaDelegate / 表达式 / 外部 Worker）
  - Script Task、Receive Task、Manual Task
  - Call Activity（调用其他流程）
  - Sub-Process / 多实例（会签/或签）
- **网关（Gateways）**：
  - Exclusive（排他，条件分支）
  - Parallel（并行）
  - Inclusive（包容）
  - Event-based
- **连接**：Sequence Flow（可带条件表达式 `${approved == true}`）

国内常见场景：串行审批、会签（多实例 + completionCondition）、或签、驳回（跳转或变量控制）、条件分支。

## 4. 相关监听器

两类主要监听器（可配置 class / expression / delegateExpression）：

Execution Listener（执行监听器）  
可挂在流程、活动、网关、顺序流上。  
事件：`start`、`end`、`take`（顺序流）。  
实现 ExecutionListener`，在 `notify(DelegateExecution) 中写逻辑。  
用途：流程开始/结束统一处理、节点进入/离开埋点、流转时记录。

Task Listener（任务监听器）  
仅用户任务。  
事件：`create`、`assignment`、`complete`、`delete`。  
实现 TaskListener`，在 `notify(DelegateTask) 中写逻辑。  
用途：动态设置候选人、发通知、SLA 初始化、完成时业务回调。

也可用 Parse Handler 全局自动给符合条件的节点加监听器。

## 5. 怎么动态控制流转

常见方式：

1. **流程变量 + 条件表达式**（最常用）  
   在网关出线或顺序流上写 `${变量名 == 值}`，完成任务时传入变量控制走向。

2. DynamicBpmnService  
   运行时修改节点属性、候选人、条件等（不改部署的定义）。

3. RuntimeService.changeActivityState() / 跳转  
   强制把执行从当前活动迁移到目标活动（驳回、跳过、任意跳转）。注意处理多实例、并行分支的副作用。

4. 多实例 + completionCondition  
   会签/或签动态人数、提前结束条件。

5. 信号/消息/事件  
   外部触发中间捕获事件或边界事件改变路径。

6. **CMMN 案例模型**（更适合高度动态场景）  
   计划项动态启用/禁用，比纯 BPMN 更灵活。

7. 企业版扩展  
   动态注入片段、Process Instance Migration 等。

生产中驳回/跳转建议封装成统一服务，并记录历史原因。

## 6. 全局监听器、执行监听器、任务监听器 

### 1. 核心区别对比

| 对比项               | 全局监听器（Event Listener）                                                 | 执行监听器（Execution Listener）                                    | 任务监听器（Task Listener）                                                  |
| -------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **接口**             | `FlowableEventListener`                                                      | `ExecutionListener`                                                 | `TaskListener`                                                               |
| **作用范围**         | **引擎全局**，监听所有流程/任务/作业等引擎级事件                             | 流程定义中的**执行路径**（流程实例、活动、网关、顺序流）            | **仅用户任务（User Task）**                                                  |
| **绑定方式**         | 代码配置到 `ProcessEngineConfiguration`，**无需在 BPMN 中绑定**              | 在 BPMN 节点或流程上配置（class / expression / delegateExpression） | 只能作为 User Task 的子元素配置                                              |
| **主要事件**         | 引擎级：流程启动/结束、任务创建/完成、作业执行、实体变更等（事件类型非常多） | `start`、`end`、`take`（顺序流被执行时）                            | `create`、`assignment`、`complete`、`delete`（部分版本还有 update、timeout） |
| **可访问对象**       | `FlowableEvent`（可转型获取具体实体）                                        | `DelegateExecution`（流程执行上下文、变量）                         | `DelegateTask`（任务属性、候选人、办理人、表单等）                           |
| **典型用途**         | 全局日志、审计、统一消息推送、监控、跨流程统计                               | 流程开始/结束统一处理、节点进入/离开埋点、流转时业务逻辑            | 动态设置办理人/候选人、发待办通知、任务完成回调、SLA 处理                    |
| **是否可见于流程图** | 不可见                                                                       | 可在设计器中配置                                                    | 可在设计器中配置                                                             |

### 2. 详细说明与联系

**1. 执行监听器（Execution Listener）**
- 监听**流程执行生命周期**。
- 可挂在：整个流程、任意活动（包括用户任务、服务任务）、网关、顺序流上。
- 事件含义：
  - `start`：活动或流程开始执行时
  - `end`：活动或流程结束时
  - `take`：顺序流被选中执行时
- 特点：拿不到完整的任务操作（如候选人列表），但能操作流程变量、执行对象。
- 适用：流程级统一逻辑、非用户任务节点的监听、流转控制辅助。

**2. 任务监听器（Task Listener）**
- 专门针对**人工任务生命周期**。
- 只能配置在 User Task 上。
- 事件含义：
  - `create`：任务创建完成后（属性已设置）
  - `assignment`：任务被分配办理人后
  - `complete`：任务完成时
  - `delete`：任务即将被删除时
- 特点：可以直接操作 `DelegateTask`（设置 assignee、候选人、dueDate、优先级、本地变量等）。
- 适用：动态分配人、发送待办/已办通知、任务级业务校验或回调。

**3. 全局监听器（FlowableEventListener）**
- 真正的“全局”监听，注册在引擎级别，对**所有已部署的流程**生效。
- 不需要在每个 BPMN 文件里重复配置。
- 能监听到更底层、更细粒度的引擎事件（流程实例创建、任务实体更新、作业失败等）。
- 适合：系统级横切关注点（统一日志、审计、消息总线、指标采集）。
- 注意：实现时要判断事件类型和实体类型，避免不必要的逻辑执行；事务敏感时需注意异常处理。

### 3. 它们之间的联系与协作

- **层级关系**：
  - 全局监听器 → 引擎级（最外层）
  - 执行监听器 → 流程/活动执行级
  - 任务监听器 → 用户任务级（最细）
- **用户任务上的执行顺序**（常见情况）：
  1. 执行监听器的 `start`
  2. 任务监听器的 `create` → `assignment`
  3. （用户处理任务）
  4. 任务监听器的 `complete`
  5. 执行监听器的 `end`
- **互补使用**：
  - 需要操作任务属性（办理人、候选人）→ 用**任务监听器**
  - 需要在任意节点或流程开始/结束做通用逻辑 → 用**执行监听器**
  - 需要跨所有流程统一处理（日志、通知、审计）→ 用**全局监听器**
- **动态/全局添加方式**：
  - 通过 `BpmnParseHandler` 在解析 BPMN 时自动给符合条件的节点加执行监听器或任务监听器（实现“全局配置但局部生效”）。
  - 运行时也可通过动态修改模型添加监听器（较少用）。

### 4. 选型建议（实际开发）

- **流程开始/结束统一处理业务数据** → 执行监听器（挂在 process 或结束事件）
- **用户任务动态分配人 / 发消息** → 任务监听器
- **所有流程都要记录操作日志 / 推送消息** → 全局监听器（`FlowableEventListener`）
- **不想在每个流程图里重复配置** → 用 Parse Handler 自动注入执行/任务监听器，或直接用全局事件监听器

三者可以同时存在，互不冲突。生产中常见组合是：全局监听器做系统级监控 + 执行监听器做流程级钩子 + 任务监听器做人机交互逻辑。

## 6. 生产环境需要做什么

- **数据库**：使用外部生产级数据库（PostgreSQL / MySQL / Oracle 等），关闭 H2；配置合适连接池；建议 Read Committed Snapshot 隔离级别（部分库）。
- **历史级别**：`history-level: full`（或 audit），满足审计；定期归档/清理历史表，避免无限膨胀。
- **异步执行器**：开启并调优线程池（`async-executor.enabled=true`，core/max pool、queue-capacity）。
- **集群**：多实例 + 负载均衡；异步作业用共享 DB 锁；Elasticsearch（如用）做集群。
- **身份**：关闭内置 IDM（`idm-enabled=false`），对接企业用户/权限体系。
- **配置**：关闭自动建表更新（生产用迁移脚本）；合理 JVM 内存、连接池；开启监控（指标、死信作业、失败任务）。
- **安全与稳定**：表达式严格模式、事务超时、速率限制、沙箱配置（防止无限循环）；文件存储用外部（不要全塞 DB BLOB）。
- **运维**：使用 Flowable Control（或自建）查看/修复卡住实例、重试作业、变量修正、状态迁移；做好备份、版本化部署、灰度。
- **性能**：流程定义缓存、避免过大变量、异步节点处理重逻辑、定期清理运行时垃圾数据。
- **高可用**：至少 2 节点 + LB；数据库高可用；监控资源（CPU/内存/DB 连接/作业堆积）。