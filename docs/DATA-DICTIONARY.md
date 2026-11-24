# 航次数据定义

四份 UTF-8 CSV 支持首行 BOM 与任意表头列序。所有列必填。空单元格与空值哨兵分别隔离，正文字段 `null` 作为普通文本参与校验。文件为空、纯空行、仅表头分别返回 `EMPTY_FILE`、`BLANK_FILE`、`HEADER_ONLY`，无停工或账单可合法提交仅表头文件。入站按逻辑 CSV 记录遍历，保留起始物理行号。每源上限 250,000 字符。

| 原件 | 字段与定义 | 去重键 |
|---|---|---|
| events | `event_id` 原形字符串，`kind` 为 READY、NOR、LOAD_START、LOAD_END，`time` 带偏移且为整分钟，`party` 为 PORT 或 SHIP | event_id |
| stops | `stop_id` 原形字符串，`kind` 为 RAIN、HOLIDAY、GAP，`start/end` 为带偏移的分钟时间 | stop_id |
| terms | `version` 字符串，`start/end` 为生效窗，`priority` 越高越优先，`wait_min/allow_min/tier1_min` 为非负整分钟，费率为美元/分钟 | version |
| invoice | `tier` 为 1 或 2，`minutes` 非负整分钟，`usd` 为非负美元 | tier |

时间在比较前统一 UTC，所有时间区间采用 `[start,end)`。港方准备后才采纳船方 NOR，允许准备与送达同分钟。通知时点选合同，最高优先级并列报错。起钟为通知加等待，结束取有效港方完成记录。停工裁决为缺证 > 假日 > 雨停，同时保存落选停工及行号。期满后仍按同一规则裁决区间。

计时额度只消耗可计分钟。滞期第一档达到档内分钟上限后切到第二档。美元计算使用 Decimal，数值输出两位字符串。差值为港方应计减船方实见，档位缺单或冲突时总差值为 `null`。重复业务键比较归一值，一致则保留首行，矛盾则全组隔离。

运行 ID 根据规则版本、源文本 SHA-256、参数计算。SQLite 唯一主键及事务保存一份快照。证据包完整性摘要使用排序键、UTF-8、紧凑 JSON，供接收人核对传输完整性。
