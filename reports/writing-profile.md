# Writing Profile / Analytics

> Initial baseline: 2026-08-27. After merge, GitHub Actions regenerates this report from article front matter, `ideas/published.md`, and metric snapshots.

## Overview

- Published articles: **3**
- Last published: **2026-08-27**
- Average publish interval: **1.5日**
- Tracked article drafts/reviews/published: **5**

## Technology Mix

Current published articles still use the older front matter schema, so `domains` / `languages` / `technologies` are intentionally shown as unclassified until metadata is explicitly added.

- Topics: GitHub (2), GitHubActions (2), GitHubAPI (2), Python (2), 個人開発 (2), ai-development (1), individual-development (1), github (1)
- Domains: Unclassified (3)
- Languages: Unclassified (3)
- Technologies: Unclassified (3)
- Portfolio signals: Unclassified (3)

## Recent Articles

- 2026-08-27 — [GitHubプロフィールをライブな開発ダッシュボードにしてみた](https://qiita.com/mizzz-ivr/items/b5cc51f17c9d9e69f630)
- 2026-08-26 — [GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた](https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a)
- 2026-08-24 — [AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話](https://qiita.com/mizzz-ivr/items/44cd3077d732eea1bf6e)

## Popular Articles

- External metrics snapshot is not available yet. The daily workflow will populate likes and other available metrics after merge.

## Data Quality baseline

- `github-profile-daily-activity`: `published.md`では公開済みだがfront matterは `status: review`
- `github-profile-daily-activity`: `published.md`にQiita URLがあるがfront matterは空
- `github-profile-live-dashboard`: `published.md`では公開済みだがfront matterは `status: review`
- `github-profile-live-dashboard`: `published.md`にQiita URLがあるがfront matterは空
- Published articles do not yet declare `domains` / `languages` / `technologies`
- Existing published articles do not yet consistently declare `published_at`

These findings are intentionally not auto-fixed. Article metadata remains author-controlled.

## Review Hints

- `Unclassified` が多い軸は、次回の記事更新時にfront matterを整備する
- 30/90日単位でtopic / domain / languageの偏りを見る
- metrics snapshotが蓄積したら、likesの絶対値だけでなく7日/30日の増分を見る
- Portfolio用途では、記事数より `portfolio_signals` とsource repositoryの対応を重視する
