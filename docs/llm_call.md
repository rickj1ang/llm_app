# 朴素的LLM call

## 需要用到的第三方包
```python
import openai
```
没了

## 用到的模型
阿里 qwen3 flash 商用
所以如果想一起做这个项目的话，需要有一个alibaba bailian的api key

## 所需要的包管理工具
[uv](https://github.com/astral-sh/uv)

## 需要的环境变量
```bash
export DASHSCOPE_API_KEY="your_api_key"
```

## 提前需要的命令
拉取这个仓库，或者自己在一个文件夹中运行
```bash
uv init
```

```bash
uv add openai
```

## 流程
1. 首先我们可以发出一次，朴素的只包含一个user message的llm call，和qwen模型打一个招呼
2. 其次，我们可以添加一个system prompt， 来体验system prompt的权利
3. 日志是很重要的东西，我们把重要的东西log出来
4. 探索一下``OpenAI.chat.completions.create()``方法，看都有哪些参数可以设置
5. 调整一下temp，看一下temp的作用（很有可能体现不出来）
6. 调整一下max_tokens，看一下max_tokens的作用
7. 测试一下服务端缓存（短prompt是没有的）
8. 玩一下流式传输
9. 测试一下是否能回答“我是谁这个问题
