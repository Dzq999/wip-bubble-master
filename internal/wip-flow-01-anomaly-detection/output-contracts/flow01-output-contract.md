# Flow 01 Output Contract Index

Flow 01 输出契约已拆分为两个文件：

- `flow01-text-output-contract.md`：说明用户可读 Markdown 的标题结构和每一部分内容方向。
- `flow01-json-output-contract.md`：说明展示层使用的轻量结构化 JSON，按 `content.containers[].sections[].items[]` 循环渲染。

执行 `wip-flow-01-anomaly-detection` 时必须同时遵守这两个契约。

如果本文件、prompt 或示例与上述两个契约有冲突，以拆分后的两个契约为准。
