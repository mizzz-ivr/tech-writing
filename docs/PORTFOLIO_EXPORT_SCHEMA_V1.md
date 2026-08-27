# Writing Portfolio Export Schema v1

`data/exports/writing-portfolio.json` のconsumer向けschema referenceです。

## Top-level

```json
{
  "schema_version": 1,
  "as_of": "YYYY-MM-DD",
  "summary": {},
  "coverage": {},
  "recent_articles": [],
  "notable_articles": [],
  "export_quality": {}
}
```

## Compatibility

- `schema_version` が `1` の間は既存fieldの意味を破壊しない。
- consumerは未知fieldを無視する。
- required field削除、型変更、意味変更はschema versionを上げる。
- `as_of` は生成時刻ではなくanalysis基準日。

詳細なSecurity / generation policyは `docs/PORTFOLIO_EXPORT.md` を参照する。
