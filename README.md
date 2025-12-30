# TRPG 日志转小说工具

将 AI TRPG 聊天记录（`.jsonl` 格式）转换为：

- **纯净小说版**：只保留故事叙述内容，去除选项、系统思考、标签等，适合直接阅读或出版。
- **原始全记录版**：完整保留所有 AI 输出（包括 `<TEXT>`、`<thinking>` 等），适合存档或调试。

## 功能特点

- 智能提取最后一个完整的 `<TEXT>...</TEXT>` 内容（排除 thinking 中的干扰）
- 自动删除开头的 `[遵守<optimize_input>...]` 系统指令
- 自动移除玩家选项 `<Options>...</Options>`
- 将平行事件分隔符转为 `---`
- 人物卡自动用 YAML 代码块高亮
- 支持命令行参数，灵活指定输入输出文件

## 安装要求

- Python 3.7+
- 无需额外依赖（仅用标准库）

## 使用方法

```bash
# 基本用法（使用默认输出文件名）
python convert_trpg_log.py "投机艺术.jsonl"

# 自定义输出文件名
python convert_trpg_log.py "冒险记录.jsonl" -s "第一卷：王都篇.md" -r "完整原始记录.md"

# 不跳过系统范例消息（一般不需要）
python convert_trpg_log.py chat.jsonl --no-skip-examples

# 查看帮助
python convert_trpg_log.py -h！
