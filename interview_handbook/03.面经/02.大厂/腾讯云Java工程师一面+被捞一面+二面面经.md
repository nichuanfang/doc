# 腾讯云Java工程师一面 + 被捞一面 + 二面面经

## 【一面】全程55min


1. 先自我介绍一下吧
2. Java1.8 的新特性？你说到了 Lambda 表达式，你说说它的优缺点？
3. Java 8 的 Stream 流用过吗？有什么特点？
4. 线程池创建的方式有哪些？`ThreadPoolExecuter` 的参数有哪些？
5. `ArrayList` 和 `LinkedList` 的区别在哪里？`Queue` 与 `Deque` 的区别？
6. `HashMap` 和 `TreeMap` 区别?
7. 假设有一个10W的数据请求，你会有什么方法来实现这些数据的增删改查？
8. 数据库的三大范式是什么？
9. MyISAM 和 InnoDB 的区别?
10. MySQL主键索引和普通索引的区别是什么？谁的性能更好一些？如果是在10W级的数据下，谁的性能更好些？
11. 介绍一下联合索引吧？
12. 以（a,b,c)为例，在什么情况下，单查 b 也能够命中联合索引？
13. 算法题：手写代码实现单向链表的结构体，完成增删改查。
14. 反问环节：你有什么问题想问我的不？



面试总结：感觉问题的题目不是太难，只怪自己太菜，基础没掌握好，面试官人不错，要是有人捞，我还想再来一次！第二天流程已结束。。



好家伙，不知道发生了什么，我又开始了新的流程，这难道就是传说中的二战！！！还是腾讯云。



## 【一面】全程46min


1. 自我介绍，
2. 接着就是来俩算法题：题1：统计一串字符中，重叠字符出现的次数。（如AAABBBCC，输出A_3_B_3_C_2）题2：求两个字符的最长公共子串
3. 你用过哪些数据库？MySQL数据库的存储引擎了解过哪些？这些存储引擎的特点是什么？
4. MySQL 默认是什么存储引擎，为啥用这个？
5. InnoDB和MyISAM的有啥区别？和MEMORY呢？
6. InnoDB为啥索引的数据结果要用B+树？
7. 为啥不用Hash索引?Hash索引查找的时候不是更快吗？
8. 网络编程了解过吗？说说如何创建一个Socket连接
9. C++的基本数据结构了解过吗？
10. 反问环节：你有什么问题想问我的不？



## 【二面】全程43min


今天上午突然给我发邮件让我下午二面，这霸道总裁的通知风格。。。



1. 看你有个比赛，你这个比赛里面做的什么？（15min）
2. 你还写过哪些应用程序，说说看？数据存储用的什么，web服务器用的什么？
3. C++了解过吗？
4. 软件设计师什么时候考的？？
5. 写过多进程和多进程吗？都在什么情况下用过？遇到了什么困难不？
6. 有没有 Linux 下的编程经验？
7. Linux常用命令了解哪些？
8. 网络编程用过吗？Sokect？
9. Linux中的epoll和select这些多路复用了解过吗？
10. 说说五层网络模型吧，说说对应的协议吧
11. 抓过网络包吗？
12. 如果要设计一个快速插入和查找的数据结构，你会用什么结构？Hash冲突的解决方法？
13. 有一个容量为N的数组，里面存放了N个数，每个数的取值范围是1~N，有没有什么快速办法判断是否有重复元素，哪个元素重复了？空间复杂度要求是O(1)
14. 求二叉树深度的算法呢？说说看？时间和空间尽可能的小
15. 设计模式了解过吗？了解一下
16. UML类图理解的怎么样？画个类图吗？
17. 云计算的知识了解吗？容器用过吗？大数据套件了解过吗？ELK了解过吗？看过开源架构系统的代码吗？（这全是知识盲区啊。。。）
18. 分布式存储了解过吗？
19. 一个进程的栈大小是多少知道吗？打开文件的上限是多少？
20. 你觉得你擅长做什么业务？
21. 反问环节



总结：整个过程主动补充有点少，导致场面数次陷入安静的尴尬场面，最长的一次甚至长达30多秒。以后的面试还是要多多扩展自己讲的内容。



文|牛客网：牛客71576213号



## 参考答案


上面的绝大部分问题，你都可以在下面的这几篇文章中找到答案。



1. [Java8 新特性实战](https://javaguide.cn/java/new-features/java8-common-new-features.html)
2. [Java 线程池详解](https://javaguide.cn/java/concurrent/java-thread-pool-summary.html)
3. [Java集合常见知识点&面试题总结(上)](https://javaguide.cn/java/collection/java-collection-questions-01.html)
4. [Java集合常见知识点&面试题总结(下)](https://javaguide.cn/java/collection/java-collection-questions-02.html)
5. [数据库基础知识](https://javaguide.cn/database/basis.html)
6. [MySQL知识点&面试题总结](https://javaguide.cn/database/mysql/mysql-questions-01.html)
7. [MySQL 索引详解](https://javaguide.cn/database/mysql/mysql-index.html)
8. [后端程序员必备的 Linux 基础知识总结](https://javaguide.cn/cs-basics/operating-system/linux-intro.html)
9. [OSI 和 TCP/IP 网络分层模型详解（基础）](https://javaguide.cn/cs-basics/network/osi&tcp-ip-model.html)
10. [《Java 面试指北》](https://mp.weixin.qq.com/s?__biz=Mzg2OTA0Njk0OA==&mid=2247519384&idx=1&sn=bc7e71af75350b755f04ca4178395b1a&chksm=cea1c353f9d64a458f797696d4144b4d6e58639371a4612b8e4d106d83a66d2289e7b2cd7431&token=660789642&lang=zh_CN&scene=21#wechat_redirect)



> 更新: 2022-05-29 15:24:50  
> 原文: <https://www.yuque.com/snailclimb/mf2z3k/lw5kph>