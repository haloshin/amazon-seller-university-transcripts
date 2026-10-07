# 贡献与纠错

欢迎提交有证据的错字、漏句、时间定位和校注修正。请附课程原标题、语言、时间戳、当前文字、建议文字，以及可核对的官方来源。可直接使用[纠错 Issue 模板](https://github.com/haloshin/amazon-seller-university-transcripts/issues/new?template=correction.yml)。

原音与原画面优先；另一语言版本和当前政策只作对照。原课程中的口误、算例矛盾和历史建议应在校注中说明，不要静默改写成当前说法。

修改正文时，同步更新 Markdown、TXT、VTT；校注单独保存。不要把猜测写成确定原文。不要提交视频、音频片段、官方 PDF、账号信息、订单数据、密钥、Cookie 或内部工作路径。

本地校验仅依赖 Python 3 标准库：

```bash
python3 scripts/verify.py
```

在明确更正内容并同步相关文件后，更新内容指纹与清单，再检查：

```bash
python3 scripts/verify.py --refresh
python3 scripts/verify.py
```

刷新指纹不表示语义校准通过；它只使文件清单与当前已审阅文件一致。校验检查课程数量、语言、正文/字幕一致性、字幕时间、链接与文件指纹，不判断课程事实或听辨准确率。
