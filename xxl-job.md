# XXL-JOB

**XXL-JOB** 是一个轻量级分布式任务调度平台（作者许雪里），核心设计目标是开发迅速、学习简单、轻量级、易扩展。它把**调度**和**任务执行**解耦：调度中心负责触发，执行器负责业务逻辑。

GitHub：https://github.com/xuxueli/xxl-job  
官方文档：https://www.xuxueli.com/xxl-job/

---

## 一、整体架构

| 组件                          | 职责                                                                                                   |
| ----------------------------- | ------------------------------------------------------------------------------------------------------ |
| **调度中心（xxl-job-admin）** | 任务 CRUD、调度触发、路由选择、日志监控、失败重试/告警。自身不跑业务代码，支持集群（共享同一 MySQL）。 |
| **执行器（Executor）**        | 接收调度请求，执行 `@XxlJob` 标注的方法或 GLUE 代码，回调结果。支持集群部署。                          |
| **数据库**                    | 存储任务信息（`xxl_job_info`）、执行器注册（`xxl_job_registry`）、调度日志（`xxl_job_log`）等。        |

**核心通信**：调度中心通过 HTTP（默认基于 Netty 内嵌 Server，端口可配，常用 9999）向执行器发送 `run` 请求；执行器执行完后回调调度中心。

---

## 二、核心代码实现原理

### 1. 执行器注册与心跳（服务发现）

执行器启动后，`ExecutorRegistryThread` 每隔 **30s** 向调度中心发送注册/心跳请求（`adminBiz.registry`）。

调度中心 `JobRegistryHelper` 定期扫描：
- 超过 **90s** 无心跳的执行器标记为离线并移除。
- 更新 `xxl_job_group` 中的在线地址列表。

```java
// 简化注册逻辑
while (!toStop) {
    adminBiz.registry(registryParam);  // 上报 appname + address
    TimeUnit.SECONDS.sleep(30);
}
```

### 2. 任务调度（时间轮 + 预读）

调度中心启动多个后台线程（`XxlJobScheduler.init`）：

- `JobScheduleHelper`：核心调度。
- `JobTriggerPoolHelper`：触发线程池（快/慢隔离）。
- `JobRegistryHelper`、`JobFailMonitorHelper`、`JobCompleteHelper` 等。

**调度流程**（`JobScheduleHelper`）：

1. 每 **5s** 扫描一次 `xxl_job_info`，预读「下次触发时间 ≤ 当前时间 + 5s」的任务（预读窗口保证准时）。
2. 使用 **MySQL 悲观锁**（`SELECT ... FOR UPDATE` on `xxl_job_lock`）保证集群中只有一个节点真正调度，避免重复触发。
3. 根据时间差处理：
   - 已过期较久：按「调度过期策略」处理（忽略 / 立即补偿一次）。
   - 即将到期：放入**时间轮**。
4. **时间轮**：`ConcurrentHashMap<Integer, List<Integer>>`，60 个槽对应 1 分钟的 60 秒。任务按 `triggerNextTime % 60` 放入对应槽。
5. 时间轮消费线程每秒对齐，取出当前秒（及前一秒，防止处理耗时导致跳过）的任务，交给触发线程池。

```java
// 简化时间轮放入
int ringSecond = (int) ((jobInfo.getTriggerNextTime() / 1000) % 60);
pushTimeRing(ringSecond, jobId);

// 消费时取当前 + 前一个槽，避免跨秒遗漏
for (int i = 0; i < 2; i++) {
    List<Integer> tmp = ringData.remove((nowSecond + 60 - i) % 60);
    // ...
}
```

### 3. 触发与路由

`JobTriggerPoolHelper` 维护**快线程池**（默认最大 200）和**慢线程池**（最大 100）。1 分钟内触发超过 10 次的任务走慢池，防止慢任务拖垮整体。

`XxlJobTrigger.trigger`：
1. 加载任务配置。
2. 根据**路由策略**从在线执行器列表选地址。
3. 构造 `TriggerParam`，通过 HTTP POST 调用执行器的 `/run` 接口。

常见路由策略：
- 第一个 / 最后一个
- 轮询（ROUND）
- 随机（RANDOM）
- 一致性 HASH
- 最不经常使用（LFU）/ 最近最久未使用（LRU）
- 故障转移（FAILOVER）
- 忙碌转移（BUSYOVER）
- **分片广播（SHARDING_BROADCAST）**

### 4. 执行器侧执行

执行器收到请求后（`ExecutorBizImpl.run`）：
1. 根据 `glueType` 找到对应 `IJobHandler`（Bean 模式通过 `@XxlJob` 扫描注册）。
2. 为每个 `jobId` 维护一个 `JobThread`（带阻塞队列）。
3. 按**阻塞处理策略**决定：
   - 单机串行（默认）：排队执行
   - 丢弃后续调度
   - 覆盖之前调度（中断旧线程）
4. 执行业务方法，通过 `XxlJobHelper` 记录日志、获取分片参数（`getShardIndex()` / `getShardTotal()`）。
5. 回调调度中心结果。

Bean 模式示例：

```java
@Component
public class SampleXxlJob {
    @XxlJob("demoJobHandler")
    public void demoJobHandler() throws Exception {
        XxlJobHelper.log("XXL-JOB, Hello World.");
        // 业务逻辑
        // 分片示例
        int shardIndex = XxlJobHelper.getShardIndex();
        int shardTotal = XxlJobHelper.getShardTotal();
    }
}
```

### 5. 其他重要机制

- **失败重试与告警**：`JobFailMonitorHelper` 扫描失败日志，未达重试次数则重新触发，达到后按配置发邮件告警。
- **任务结果丢失处理**：`JobCompleteHelper` 对长时间「运行中」且执行器已离线的日志主动标记失败。
- **日志清理**：定期清理过期调度日志。
- **GLUE 模式**：支持在线编写 Java / Shell / Python 等，源码由调度中心下发到执行器动态编译/执行。

---

## 三、面试常问问题（高频 + 参考答案要点）

### 基础类

1. **XXL-JOB 是什么？有哪些核心组件？**  
   轻量级分布式任务调度平台。核心：调度中心 + 执行器 + 共享数据库。调度与执行解耦。

2. **和 Spring `@Scheduled`、Quartz 的区别？**  
   - `@Scheduled`：单机，无分布式、无可视化、难动态调整。  
   - Quartz：支持集群但依赖 DB 锁，性能一般，无可视化管理台，扩展分片/失败重试需自己做。  
   - XXL-JOB：原生分布式、Web 控制台、动态启停/改 Cron、丰富路由与分片、失败重试告警、完整日志。

3. **任务有哪些运行模式？**  
   Bean 模式（推荐，代码在执行器项目里用 `@XxlJob`）、GLUE 模式（在线写代码，支持多种语言）。

### 原理类

4. **任务是如何被触发的？整体流程？**  
   调度中心 `JobScheduleHelper` 预读 → 时间轮 → 触发线程池 → 路由选执行器 → HTTP 调用 `/run` → 执行器 `JobThread` 执行 → 回调结果。

5. **调度中心如何保证集群下不重复调度？**  
   数据库悲观锁（`xxl_job_lock` 表 `FOR UPDATE`）+ 事务，同一时刻只有一个调度节点拿到锁并处理。

6. **时间轮是怎么实现的？为什么用它？**  
   60 槽 ConcurrentHashMap，按秒取模放入。消费线程每秒处理当前+前一槽。比直接 sleep 或大量 Timer 更高效，适合大量定时任务。

7. **执行器如何注册与发现？心跳机制？**  
   执行器主动注册 + 30s 心跳；调度中心 定期清理 90s 无心跳的节点。

8. **路由策略有哪些？分片广播怎么用？**  
   列出常见策略。分片广播时所有在线执行器都会执行，通过 `XxlJobHelper.getShardIndex()/getShardTotal()` 自行分片数据（如 `id % total == index`）。

### 进阶/实战类

9. **如何保证任务不重复执行 / 解决任务重叠？**  
   - 调度侧：DB 锁保证单节点调度。  
   - 执行器侧：阻塞处理策略选「单机串行」或「丢弃后续」。  
   - 业务侧：任务必须**幂等**（唯一键、状态机、分布式锁）。  
   注意：分片广播本身就会多机执行。

10. **任务执行失败怎么办？**  
    可配置失败重试次数；重试耗尽后按邮件告警；可手动重跑。

11. **执行器显示离线的常见原因？**  
    调度中心地址配错、appname 不一致、端口占用、网络/防火墙、accessToken 不匹配、心跳发不出去。

12. **快慢线程池的作用？**  
    隔离慢任务，防止长时间占用线程影响其他任务触发。

13. **如何做分片任务处理大数据量？**  
    路由选「分片广播」，在 Job 里按 `shardIndex` / `shardTotal` 切分数据范围或取模。

14. **调度过期策略、阻塞处理策略分别是什么？**  
    过期：忽略 / 立即补偿一次。  
    阻塞：单机串行 / 丢弃后续 / 覆盖之前。

15. **项目中如何集成？**  
    引入 `xxl-job-core` → 配置 admin 地址、appname、port → 声明 `XxlJobSpringExecutor` Bean → 写 `@XxlJob` 方法 → 在调度中心配置任务并启动。

---

## 四、面试回答建议

- 先画架构图（调度中心 ↔ 执行器 ↔ DB），再说注册 → 调度（时间轮 + 锁）→ 触发（路由）→ 执行 → 回调。
- 强调**解耦**、**HA**、**可视化**、**分片**这几个卖点。
- 结合自己项目说一个真实场景（如订单清理、数据同步、报表生成），并提一下幂等和监控。
- 如果被追问源码，能说出 `JobScheduleHelper`、时间轮、`JobTriggerPoolHelper` 快慢池、`ExecutorRegistryThread`、路由策略接口这几个关键点即可。

掌握以上内容，覆盖绝大多数 XXL-JOB 相关面试问题。需要具体某个类的源码细节或某个策略的实现代码，可以继续深入问。