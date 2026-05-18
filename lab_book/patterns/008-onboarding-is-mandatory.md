# 新项目必须走完整接入流程

## 发现来源
系统自省时发现：prompt_optimization 和 tweet_building 在其他 session 创建，
但没有 lab_book/entries/ 记录，没有被正式"接入"，导致知识库不完整。

## 模式
新项目创建时，必须完成以下步骤：

```
1. 创建目录结构        ← new_project.py 自动完成
2. 生成 README.md      ← new_project.py 自动完成
3. 生成 notes/progress.md  ← new_project.py 自动完成
4. 写 lab_book/entries/ 接入记录  ← new_project.py 自动完成
5. 向用户提问了解项目  ← AI 在对话中完成
6. 提出建议           ← AI 在对话中完成
```

## 为什么重要
- 没有接入记录 = 这个项目在知识库里是"隐形"的
- 没有提问 = AI 不了解项目背景，后续协助质量差
- 没有建议 = 错过了优化机会

## 验证方法
检查 lab_book/entries/ 下是否有对应的接入记录。
如果没有，说明接入流程没有走完。
