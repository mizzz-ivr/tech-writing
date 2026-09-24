---
title: "判断特化AI『Jev』、普通のLLMと何が違う？個人開発での使い道を考えてみた"
tags:
  - AI
  - Jev
  - TypeScript
  - 個人開発
private: true
updated_at: ""
id: null
organization_url_name: null
slide: false
ignorePublish: true
---

## 結論

Jevの公開ドキュメントを読んで最初に感じたのは、

**「文章を作るAI」ではなく、「アプリの途中に置く判断役」として考えると分かりやすい**

ということでした。

普通のLLMなら、

```text
入力
 ↓
LLM
 ↓
説明・文章・コード
```

のような使い方をまず思い浮かべます。

一方、JevのAPIは `state` と質問を渡し、Choice / Score / Noulなどの**構造化された判断**を受け取る設計です。

```text
アプリの状態
    ↓
   Jev
    ↓
構造化された判断
    ↓
アプリ側が次の処理を決める
```

今回はアカウントを作ってベンチマークする記事ではありません。

公開されているAPI仕様とユースケースを読みながら、

**「これ、自分の個人開発ならどこに入れられそう？」**

という視点で使い道を考えてみます。

## Jevって何？

JevのREST APIドキュメントでは、Jevはエージェントのメインモデルを置き換えるものではなく、ツール実行・Web閲覧・長文推論を行わず、判断結果を構造化して返すものとして説明されています。

Native Decisionsでは、

- `choice`: 候補から1つを選ぶ
- `score`: 順序付きの段階で評価する
- `noul`: YESである確率を0〜1で返す

という質問を扱えます。

たとえば公式ドキュメントに近い形なら、

```json
{
  "state": {
    "environment": "production",
    "operation": "delete old records",
    "backup": "unknown"
  },
  "questions": {
    "action": {
      "type": "choice",
      "instructions": "Choose the safest next action.",
      "criteria": {
        "allow": "Proceed",
        "review": "Require human review",
        "deny": "Do not proceed"
      }
    },
    "needs_human_review": {
      "type": "noul",
      "instructions": "Does this require human review?"
    },
    "risk": {
      "type": "score",
      "instructions": "Score the operational risk.",
      "criteria": ["Low", "Moderate", "High", "Critical"]
    }
  }
}
```

のように、同じstateに対して複数種類の判断をまとめて質問できます。

ここが普通のチャットUIを触る感覚とはかなり違います。

## すでに「判断用」のAPIが用意されている

さらに面白かったのが、Native Decisionsだけではなく用途別のpresetが用意されていることです。

公開APIには、たとえば次のようなものがあります。

| 用途 | API |
| --- | --- |
| ツール実行を許可・確認・レビュー・拒否する | `tool-guard` |
| 利用可能なモデルから選ぶ | `model-route` |
| タスクの進め方を判断する | `route` |
| 与えられた証拠が主張を支えるか確認する | `research` |
| 本当に目的を達成したか確認する | `completion` |
| 独自のChoice / Score / Noulを定義する | `decisions` |

つまり「AIに判断させる」といっても、全部を自由文プロンプトから作る必要はありません。

特に `tool-guard` と `completion` は、AIエージェントを使っているとかなり気になるところでした。

## 使い道1：GitHub Issueの優先順位付け

最初に思いついたのはIssueや運用タスクのトリアージです。

たとえば、

```json
{
  "title": "PostgreSQL backup is stale",
  "age_hours": 50,
  "threshold_hours": 25,
  "application_status": "running"
}
```

という状態があったとします。

ここで、

```text
今すぐ対応
今日中
今週
保留
```

のどれにするかをChoiceで判断させる。

さらにScoreで影響度、Noulで「人間へ通知すべきか」を同時に判断する、といった使い方が考えられます。

もちろん、バックアップが50時間古ければ必ずこの優先度、というルールが決まっているなら普通のif文で十分です。

Jevが面白そうなのは、

- サービス自体は動いている
- バックアップだけ古い
- 復旧手段が別にある
- メンテナンス時間が近い
- 他にも障害が発生している

のように、**複数の状態をまとめて判断したい場面**です。

## 使い道2：AIエージェントの「完了しました」をチェックする

個人的に一番使ってみたいのがこれです。

AIエージェントへ、

> 記事を作成して公開まで進めて

と頼んだとします。

しばらくすると、

> 完了しました。

と返ってくる。

でも実際には、

```text
✓ 原稿を書いた
✓ GitHubへcommitした
✗ 公開URLを確認していない
```

かもしれません。

Jevには `completion` のpresetがあり、

```json
{
  "objective": "Qiita記事を公開する",
  "completed_work": [
    "記事本文を作成した",
    "GitHubへcommitした"
  ],
  "verification": [],
  "known_gaps": [
    "Qiitaの公開URLは確認していない"
  ]
}
```

のように、目的・完了した作業・検証・既知の不足を渡して、`complete / verify_more / incomplete` の判断に使えます。

これをAIエージェントの最後に挟むと、

```text
AI Agent
   ↓
作業を実行
   ↓
「完了しました」
   ↓
  Jev
   ↓
complete / verify_more / incomplete
   ↓
必要ならAgentへ戻す
```

という構成が作れそうです。

コードを書くAIと、**「本当に終わった？」を確認する判断役**を分ける発想です。

## 使い道3：危険なツール実行の前に置く

Jevには `tool-guard` もあります。

これはJev自身がツールを実行するものではありません。

「このツール呼び出しを実行していい？」という判断を、

```text
allow
confirm
review
deny
```

のような形で返し、実際にどうするかはアプリ側が決めます。

AIエージェントが、

```text
ファイルを読む
Issueを作る
PRを作る
本番DBを変更する
請求処理をする
```

といった複数のツールを使える場合、すべて同じ扱いにするのは怖いです。

そこで、

```text
Agent
  ↓
Tool Call
  ↓
Jev Tool Guard
  ↓
allow ─────→ 実行
confirm ───→ ユーザー確認
review ────→ 人間レビュー
deny ──────→ 中止
```

のようなゲートを挟む。

個人開発でも、AIエージェントに操作権限を増やしていくほど、この手の層は欲しくなりそうです。

## 使い道4：どのAIモデルに投げるか決める

もう1つ面白いのが `model-route` です。

たとえばアプリ側に、

```text
fast-model
reasoning-model
```

があるとします。

全部reasoning modelへ投げれば品質は上げやすいですが、コストやレイテンシも増えます。

逆に全部fast modelへ投げると、複雑なタスクでは力不足になるかもしれません。

そこで、

```json
{
  "task": "大量のコンテキストを含む複雑なレビュー",
  "candidates": [
    {
      "id": "fast-model",
      "description": "高速・低コスト"
    },
    {
      "id": "reasoning-model",
      "description": "高品質・高コスト"
    }
  ],
  "priorities": [
    "quality",
    "cost"
  ],
  "stakes": "high"
}
```

のような情報からモデルを選ばせる。

LLMを呼び出す**前**にJevを置く構成です。

```text
User Request
     ↓
    Jev
     ↓
 ┌───┴────┐
Fast    Reasoning
Model     Model
```

複数モデルを使い分けるサービスなら、かなり分かりやすい用途だと思いました。

## 使い道5：HertaみたいなDiscord Botなら？

自分の個人開発に当てはめると、Discord Botにも入れられそうです。

たとえば投稿や操作要求を受け取って、

- どの処理へルーティングするか
- モデレーター確認が必要か
- 自動処理してよいか
- AI回答が必要か
- 高性能モデルを使う必要があるか

を先に判断する。

```text
Discord Event
     ↓
    Jev
     ↓
 ┌───┼────────┐
Rule  Fast LLM  Strong LLM
 │       │          │
 └───────┴──────────┘
          ↓
       Response
```

「とりあえず全部LLMに投げる」より役割がはっきりします。

Jevの公式ユースケースにも、Intent Routing、Content Moderation、Invoice Classification、CSV Validation、Claim Verificationなど、生成ではなく**分類・評価・ルーティング**を中心にした例が並んでいます。

## じゃあif文の代わりなの？

ここは少し違うと思っています。

たとえば、

```ts
if (backupAgeHours > 24) {
  alert();
}
```

で済むなら、Jevを呼ぶ必要はありません。

ルールが明確で、境界値も人間が決められるならコードにした方が速く、安く、予測可能です。

Jevを検討したくなるのは、

```text
明確なルール
────────────
if / switch

複数の曖昧な情報から判断
────────────
Jev

調査・説明・生成・複雑な推論
────────────
LLM / Agent
```

くらいに分けたときの真ん中です。

**if文にするには曖昧。でも長文を生成するLLMを呼ぶほどでもない。**

この領域を「判断」という独立した処理として切り出すのが、Jevの面白いところだと感じました。

## 判断結果をそのまま権限にはしない

一方で、Jevが `allow` を返したから本番DBを変更する、のような実装は避けたいです。

JevのAPIドキュメントでも、probabilityはsignalとして扱い、authorizationとして扱わないよう明記されています。

なので実際に組むなら、

```text
Jev
 ↓
判断結果
 ↓
アプリ側のルール
 ↓
必要なら人間承認
 ↓
実行
```

という形にします。

特に、

- 削除
- 決済
- 本番環境変更
- 権限変更
- 個人情報に関わる処理

などは、Jevに限らずAIの判断だけで直接実行させない設計にしたいところです。

## 実際に触らなくても、APIを見ると思想がかなり分かる

今回はアカウントを作ってJevを実行するところまではやっていません。

そのため、この記事では精度や実測レイテンシについて評価しません。

公式サイトではミリ秒級の応答や構造化判定が紹介されていますが、これはあくまで提供側が公開している仕様・説明として捉えています。

それでもAPIを眺めるだけで、

**「生成AIをどこで使うか」ではなく、「ソフトウェアの判断をどこまでAIへ切り出すか」**

という考え方が見えてきました。

特に、

```text
Agentが作業する
        ↓
Jevが完了を判断する
        ↓
不足していたらAgentへ戻す
```

という構成は、実際の個人開発でも試してみたいです。

## まとめ

Jevの公開仕様を読んで、使い道として特に気になったのは、

- Issueや運用タスクのトリアージ
- AIエージェントの完了判定
- Tool Callのガード
- AIモデルのルーティング
- Discord Botなどでの分類・判断

でした。

Jevは普通のLLMの代替というより、**LLMやエージェントの前後に置く「判断レイヤー」**として考えると面白そうです。

```text
入力
 ↓
Jev ── 判断
 ↓
LLM / Agent ── 生成・作業
 ↓
Jev ── 完了確認
 ↓
アプリ
```

何でもLLMに投げるのではなく、

**「これは生成してほしいのか、それとも判断してほしいだけなのか？」**

を分ける。

Jevを調べていて、一番面白いと思ったのはそこでした。

---

## 参考

- Qiita「あなたはもう試した？判断特化AI『Jev』で遊ぼう！」
- Jev API REST Docs
- Jev Use Cases
