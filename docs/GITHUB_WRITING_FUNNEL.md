# GitHub → Writing Funnel

## 目的

最近のGitHub実装・Releaseから、まだ `tech-writing` のarticle / backlogとして明示的に追跡していないevidenceを見つけます。

この機能は「AIが次の記事を勝手に決める」仕組みではありません。GitHub上で確認できる実装事実を候補化し、既存のWriting Analytics / Content Opportunitiesへつなぐための前段です。

## Source of Truth

1. configured public repositoriesのGitHub API
2. `data/github-funnel/YYYY-MM-DD.json` — 日次raw snapshot
3. `articles/**` / `ideas/backlog.md` — 記事化済み・追跡中かの判定元
4. `data/analytics/writing-analytics.json` / reports — derived / regeneratable

GitHub APIのlive responseを直接Dashboardへ描画しません。必ずstored snapshotを境界にします。

## 監視Repository

`config/github-writing-funnel.yml` の明示allowlistだけを対象にします。

初期設定:

- `ivRooom/Herta`
- `mizzz-ivr/profile-signal`
- `mizzz-ivr/roomate-voice`
- `mizzz-ivr/ivmz-home`
- `mizzz-ivr/mizzz-ivr`

`mizzz-ivr/tech-writing` 自身は自己参照ノイズになるためrejectします。

refresh時にはGitHub Repository metadataを確認し、`private: false` かつ非archiveでないRepositoryは収集を拒否します。private repositoryを自動列挙しません。

## 収集対象

### merged Pull Request

`lookback_days` 内にmergeされたPRを収集します。

保存するのは:

- PR number
- title
- public URL
- merged_at

### Release

`release_lookback_days` 内のnon-draft Releaseを収集します。

保存するのは:

- tag
- name
- public URL
- published_at
- prerelease flag

### significant Issue

Issue本文から「重要そう」を推測しません。

`significant_issue_labels` に明示されたlabelを持つclosed Issueだけを対象にします。PRとして返されるIssue rowは除外します。

## Snapshot

通常:

```bash
python scripts/writing_funnel.py --refresh
```

当日のsnapshotがすでに存在する場合は再取得・再書込しません。`collected_at` だけ変わる不要commitを防ぎます。

PR validation:

```bash
python scripts/writing_funnel.py --check
```

`--check` はnetwork accessを行わず、configとstored snapshotだけを検証します。

GitHub API取得はmain / daily refreshでbest-effortです。失敗した場合も既存stored snapshotをData Mart / reportsから利用できるため、Writing Analytics全体を停止させません。

## Tracked / Untracked判定

GitHub evidence titleと、次を比較します。

- tracked article title
- backlog title

比較は`title_overlap_threshold`以上のtitle similarityだけを使います。

- overlapあり: `tracked`
- overlapなし: `untracked`

本文・diff・Repository内容から意味的重複をAI推測しません。そのためfalse negativeはあり得ますが、勝手に「記事化済み」と消すより安全側を選びます。

## 候補の並び順

単一のsignificance scoreは作りません。

明示ルール:

1. Release
2. merged Pull Request
3. configured label付きclosed Issue
4. 同じkindでは新しいevent

同一Repository・正規化titleが重複する場合は、上位kindのevidenceを代表として残します。

## Analytics統合

### Content Opportunities

`reports/content-opportunities.md` に `GitHub → Writing Funnel` sectionを追加します。

生成:

```bash
python scripts/writing_opportunities_funnel.py
```

### Data Mart

`data/analytics/writing-analytics.json` に `github_writing_funnel` を追加します。

生成:

```bash
python scripts/writing_data_mart_funnel.py
```

主なfield:

- `as_of`
- `snapshot_available`
- `monitored_repositories`
- `evidence_count`
- `untracked_count`
- `tracked_count`
- `candidates`

### Decision Dashboard

`reports/visual-dashboard.md` の上部KPIと `GitHub → Writing Funnel` sectionで確認できます。

生成:

```bash
python scripts/writing_decision_dashboard_funnel.py
```

## Security / Privacy

- private repositoryはallowlistへ入れない
- refresh時にもGitHub metadataでpublic/non-archivedを検証する
- GitHub Token用の新規Repository Secretを要求しない
- APIはpublic endpointだけを利用する
- raw snapshotへPR/Issue本文、comment、author email、Secret、Tokenを保存しない
- Public Portfolio JSON schemaは変更しない

## 運用変更

監視対象を増やす場合は、記事化候補として外部公開して問題ないpublic Repositoryだけを`config/github-writing-funnel.yml`へ追加し、PR reviewで確認します。

private→public化直後など判断が必要なRepositoryは、自動追加せず明示レビュー後にallowlistへ追加します。

## Non-goals

- private repositoryの収集
- PR diffをLLMで読んで記事titleを自動生成
- Issue本文からsignificanceを推測
- backlogへ自動追記
- 自動投稿
- GitHubのlive stateをraw snapshotなしでderived reportへ直接反映
