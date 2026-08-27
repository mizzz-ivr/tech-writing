# Zenn Books

このディレクトリはZenn GitHub Deploy対象の本を管理します。

新規作成:

```bash
npm run zenn:new:book -- --slug <12-50文字のbook-slug>
```

生成された `books/<book-slug>/config.yaml` は公開準備が完了するまで `published: false` にします。

詳細は `docs/ZENN_GITHUB_DEPLOY.md` を参照してください。
