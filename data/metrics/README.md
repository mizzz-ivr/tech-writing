# Metrics snapshots

`writing-analytics.yml` が取得した外部メトリクスを日付単位のJSONで保存します。

```text
data/metrics/
├─ README.md
├─ 2026-08-27.json
├─ 2026-08-28.json
└─ ...
```

## 方針

- 最新値で上書きせず、日次snapshotを残す
- Secret / API Tokenは保存しない
- APIが返さない値は `null`
- 外部APIの取得失敗はsnapshot内の `errors` に残す
- Zennは非公式endpoint依存のためbest-effort

この履歴を使い、将来的に7日/30日/90日増分、初速、long-tail、媒体差を分析します。
