# Notes: AI Runtime Safety Boundary

## この記事の位置づけ

- 媒体: Zenn
- 公開日: 2026-08-27
- 公開URL: https://zenn.dev/mizzz-ivr/articles/ai-runtime-safety-boundary
- GitHub Issue: #12
- 公開PR: #25
- Qiitaへの同一本文転載: しない
- 狙い: How-toではなく、実装から得た設計判断・Security境界・Trade-offを扱う

## Source of Truth確認

2026-08-27公開直前に再確認。

対象Repository: `ivRooom/Herta`

公開直前確認時main:

- `1cb53194a288482a10ef350cd16e38911fd328ed`
- latest merge: PR #347 `feat(ai): add Phase 1 artifact runtime and Discord attachment delivery`

主に確認したもの:

- `docs/AI_FOUNDATION.md`
- `docs/RUNTIME_SECRETS.md`
- `apps/bot/src/ai/factory.ts`
- `apps/bot/src/ai/factory.test.ts`
- `apps/bot/src/ai/runtime-service.ts`
- `packages/db/src/runtime-secrets.ts`
- `packages/plugin-catalog/src/ai-runtime-policy.ts`
- `packages/plugin-catalog/src/ai-service.ts`
- Studio AI Runtime Settings / Runtime Secret関連コード

## 確認済みの事実

- AI Foundation v1のimplemented providerは2026-08-27時点で`openai`のみ。
- Runtime Secret Storeの`openai.api_key`をprimary sourceとしている。
- `OPENAI_API_KEY`はSecret未登録時のみmigration fallbackとして使う。
- Secret Storeのread/decrypt/DB failureはenv fallbackへ逃がさずfail closedする。
- provider / model profile / reasoningはSecretと分離したtyped Runtime Configurationで扱う。
- Runtime Configはserver allowlistで検証し、unsupported combinationをsilent downgradeしない。
- request開始時にruntime snapshotを解決し、同一request中の前提を固定する。
- per-user / per-Guild rate limit、Guild budget、global concurrency、per-request cost capをserver-side guardとして持つ。
- global kill switchがある。
- AI disabled / credential unavailableでもBot本体を起動可能にしている。
- Provider errorは外部向けcategoryへ正規化し、Provider本文をそのまま利用者やstructured logへ返さない。
- raw prompt / raw responseはdefaultで永続保存・structured loggingしない。
- credential bootstrapのfail-closed挙動はVitestで固定されている。

## 将来構想としてのみ書くこと

以下は**実装済みと書かない**。

- Claude / Anthropic Provider対応
- Gemini Provider対応
- Kimi等の追加Provider対応
- Provider間の自動fallback / routing
- 全Provider共通の完成済みAdapter interface

記事では「現在OpenAI only。2つ目以降のProvider実装で差分が見えてからAdapter境界を固める」という設計判断として扱う。

## Qiita既存記事との差分

公開済みQiita:

1. Repository is the Source of TruthによるAI開発運用
2. GitHubプロフィールREADMEへの当日活動自動表示
3. GitHubプロフィールのライブ開発ダッシュボード化

今回の記事は、開発運用やGitHub自動化ではなく、AI Runtime内部のSecurity / Cost / Configuration設計が主題。既存3本と主題・構成・コード例が重複しない。

## 公開時に残した具体性

- Secretが「未登録」と「読めない」を分けた理由
- request-time immutable snapshot
- RateとBudgetを分けた理由
- AI subsystemだけ停止できるKill Switch
- 成功系よりfail-closedをテストへ固定したこと
- Providerが1つの段階では抽象化しすぎない判断

## 公開時に削った / 一般化した情報

- API Key / Secret値
- productionの具体的な認証情報
- private/internal URL
- 管理系Account ID等
- 不要なIssue番号やPR番号
- Herta内部だけで意味が通じる固有名詞
- 将来構想を実装済みと誤認させる表現

## Zenn topics

- TypeScript
- 生成AI
- OpenAI
- Security
- Architecture

## 公開チェック

- [x] Herta mainを再取得し、AI FoundationのProvider対応状況を再確認
- [x] `docs/AI_FOUNDATION.md` と実装差分がないか再確認
- [x] factory / runtime-service / testsの挙動を再確認
- [x] Secretや本番情報が本文へ混入していない
- [x] Claude/Geminiを実装済みと読める記述がない
- [x] Zenn GitHub Deployで下書き生成を確認
- [x] タイトルとtopicsを確定
- [x] PR #25で `published: true` をmainへmerge
- [x] 2026-08-27に公開確認
- [x] `ideas/published.md` のZenn列へURLを記録
- [x] Notionへ公開記録と今後の運用を反映

## 今後の更新方針

- 公開後の軽微修正もRepositoryをSource of TruthとしてPR経由で行う。
- Web EditorとRepositoryを同時編集しない。
- 実装状況が変わる内容を更新する場合は、必ずHerta Repositoryを再確認する。
- 2つ目のProviderを実装・検証した段階で、Provider abstractionの答え合わせ記事を次候補とする。
