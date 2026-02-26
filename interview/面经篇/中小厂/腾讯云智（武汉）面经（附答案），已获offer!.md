# 腾讯云智（武汉）面经（附答案），已获 offer!

分享一位球友面试腾讯云智（腾讯集团旗下的全资子公司）投稿的面经，主要记录了自己在面试过程中遇到的问题。校招和社招都适用，也欢迎大家多多分享自己的面经，优质面经有大红包奖励。



下面是正文。



本人在湖北的一所民办二本，学校非常一般。参加了 23 届秋招，由于寒气逼人，快到年底才拿到 offer，感谢腾讯云智！！！



## 腾讯云智（武汉）


### 一面(40min)


1. 自我介绍；
2. 项目中的 Redis 是如何使用的？
3. Redis 基本的数据结构；
4. Redis 持久化策略；
5. Redis 单线程模型；
6. 乐观锁和悲观锁（让我列举了一些悲观锁和乐观锁的实际例子，然后聊了 CAS 算法）；
7. `ReentrantReadWriteLock` 和 `StampedLock`；
8. AQS 基本介绍以及 JDK 中的应用；
9. 数据库索引结构；
10. 手写一条 sql 语句然后让判断索引是否生效；
11. 线程池核心参数，常见的饱和策略；
12. 常见的排序算法，快排原理、时间复杂度和空间复杂度。
13. 手写链表翻转；
14. 反问（个人表现、二面一般什么时候通知）。



本来以为一面凉了，结果过了两个星期收到了二面的通知。



答案：



+ [Redis 常见面试题总结(上)](https://javaguide.cn/database/redis/redis-questions-01.html)、[Redis 常见面试题总结(下)](https://javaguide.cn/database/redis/redis-questions-02.html)
+ [乐观锁和悲观锁详解](https://javaguide.cn/java/concurrent/optimistic-lock-and-pessimistic-lock.html)
+ [Java 并发常见面试题总结（中）](https://javaguide.cn/java/concurrent/java-concurrent-questions-02.html)、[Java 并发常见面试题总结（下）](https://javaguide.cn/java/concurrent/java-concurrent-questions-02.html)
+ [15 个必知的 MySQL 索引失效场景，别再踩坑了！](https://mp.weixin.qq.com/s/iBPO4Y_Q5ANSZ9iETAdMvA)
+ [十大经典排序算法总结](https://javaguide.cn/cs-basics/algorithms/10-classical-sorting-algorithms.html)
+ [反转链表(Reverse Linked List) - 力扣(LeetCode)](https://leetcode.cn/problems/reverse-linked-list/)



### 二面(40min)


1. 自我介绍
2. 项目中用到了哪些 SQL 优化手段；
3. 怎么分析 SQL 语句性能；
4. 索引底层的数据结构；
5. 你知道哪些让索引失效的情况；
6. 项目中 Jmeter 压测是怎么做的；
7. 压测的时候前几次值一般偏低，知道是什么原因吗（懒加载）；
8. 项目中是用了哪些多线程的知识；
9. 需要主线程等待子线程执行完毕后再执行，有哪些方法可以实现；
10. `sychornized` 为什么是重量级锁，从操作系统层面讲；
11. `sychronized` 的作用，出了 8 道场景题，难度较低；
12. 线程池处理任务的流程；
13. 用户输入网址到显示对应页面的全过程；
14. 输入一个域名后经历的协议；
15. DNS 解析的过程；
16. UDP 和 TCP 的区别；
17. 拥塞控制；
18. 滑动窗口机制；
19. 反问（个人表现、后续的面试流程、部门的业务方向、技术栈）。



答案：



+ [《Java 面试指北》的技术面试题篇-高并发](https://javaguide.cn/zhuanlan/java-mian-shi-zhi-bei.html)
+ [MySQL 执行计划分析](https://javaguide.cn/database/mysql/mysql-query-execution-plan.html)
+ [MySQL 索引详解](https://javaguide.cn/database/mysql/mysql-index.html)
+ [15 个必知的 MySQL 索引失效场景，别再踩坑了！](https://mp.weixin.qq.com/s/iBPO4Y_Q5ANSZ9iETAdMvA)
+ [如何利用 Jmeter 从 0 到 1 做一次完整的压测](https://mp.weixin.qq.com/s/MfYsvK_4We6bixN0laqGrg)
+ 多线程优化案例： 
    - [如何在 SpringBoot 中使用异步方法优化 Service 逻辑提高接口响应速度? - 2022](https://blog.csdn.net/weixin_43441509/article/details/119855613)
    - [CompletableFuture 原理与实践-外卖商家端 API 的异步化 - 美团技术团队- 2022](https://zhuanlan.zhihu.com/p/515993095)
+ [CompletableFuture 详解](https://javaguide.cn/java/concurrent/completablefuture-intro.html)（`allOf()`方法会等到所有的 `CompletableFuture` 都运行完成之后再返回）、[CountDownLatch 原理详解](https://www.cnblogs.com/dwlsxj/p/CountDownLatch.html)
+ [Java 并发常见面试题总结（中）](https://javaguide.cn/java/concurrent/java-concurrent-questions-02.html)、[Java 并发常见面试题总结（下）](https://javaguide.cn/java/concurrent/java-concurrent-questions-02.html)
+ [计算机网络常见面试题总结](https://javaguide.cn/cs-basics/network/other-network-questions.html)



### HR 面(20min)


1. 自我介绍；
2. 哪里人，目前是不是在武汉；
3. 对前几面面试官有什么感受；
4. 家庭情况；
5. 职业规划；
6. 大学期间参加了哪些活动；
7. 平时的学习方式；
8. 手里面还有没有其他 offer；
9. ......



到了 HR 面基本稳了，HR 面过了大概一周发了 Offer。



## 总结


腾讯云智的面试效率比较低，很慢，但面试官总体给我的感觉还可以。



听网上的人说腾讯云智是内包，不太好。不过，我个人还是非常感谢腾讯云智给了我 offer。它不嫌弃我学校不好，我也不嫌弃它可能是个内包。如果后续没有其他更好的 offer，我就去腾讯云智了。



> 更新: 2023-03-21 15:10:46  
> 原文: <https://www.yuque.com/snailclimb/mf2z3k/rbc1abk22uf4qokn>