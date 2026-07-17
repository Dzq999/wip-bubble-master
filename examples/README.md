# 总控示例

本目录只保存总控启动与返回结构模板：

- `master/start-request.json`
- `master/start-response.json`

各 Flow 的结构模板位于对应子 Skill 的 `internal/wip-flow-*/examples/`。执行时不预加载示例；仅在维护或核对当前 Flow 的结构时按需读取，且示例不参与运行或提供业务事实。
