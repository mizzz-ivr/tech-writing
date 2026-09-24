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

Jev、かなり変わってる。

普通の生成AIみたいに「文章を書いて」「コードを書いて」ではなく、**判断することに寄せたAI**。

```text
状態を渡す
   ↓
  Jev
   ↓
「どれ？」「どのくらい？」「YES寄り？」
```

最初は「判断だけして何に使うん？」と思った。

でもAPIを見ていたら、

**これ、LLMやAIエージェントの前後に置くと面白いやつでは？**

となった。

今回はアカウントを作って実測！……まではやらない。

公式のAPI仕様を読みながら、「自分の個人開発ならどこに入れられそうか」を考えてみる。

---

## 🤔 そもそもJevって何？

Jevは「判断」に寄せたAI。

普通のLLMなら、文章を書いたり、コードを書いたり、説明してもらったりする。

Jevはちょっと違う。

```text
アプリの状態
    ↓
   Jev
    ↓
  判断結果
    ↓
アプリが次の処理をする
```

自分でツールを叩くわけでもない。Webを調べるわけでもない。長文を書いてくれるわけでもない。

**判断して返す。**

潔い。

### 判断方法は3種類

Native Decisionsでは主に `choice` / `score` / `noul` を使える。

| 種類 | 何をする？ |
| --- | --- |
| `choice` | 候補から1つ選ぶ |
| `score` | 段階評価する |
| `noul` | YESの確率を0〜1で返す |

例えばこんな感じ。

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

同じ状態を渡して、「どうする？」「人間レビューいる？」「どれくらい危ない？」をまとめて聞ける。

なるほど。

**「AIに回答させる」より「アプリの分岐をAIに判断させる」感じ。**

---

## 🔥 判断用のAPIが最初からある

ここが結構おもしろかった。

Jevには自由にChoice / Score / Noulを作るだけじゃなく、用途別のpresetもある。

| API | 何を判断する？ |
| --- | --- |
| `tool-guard` | ツールを実行していい？ |
| `model-route` | どのモデルを使う？ |
| `route` | 次にどう進める？ |
| `research` | この証拠で主張を支えられる？ |
| `completion` | 本当に終わった？ |
| `decisions` | 独自の判断を作る |

この一覧を見て、一番気になったのが `completion`。

**「本当に終わった？」をAIに判断させる。**

めちゃくちゃ気になる。

---

## 🔥 使い道その1：「完了しました」を本当に信じていい？

AIエージェントを使ってると、たまにある。

自分：

> 記事作って公開まで進めて

AI：

> 完了しました！

確認する。

```text
記事本文       ✅
GitHub commit  ✅
公開           ❌
公開URL確認    ❌
```

終わってない。

**「完了しました！」じゃない。**

そこでJevの `completion`。

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

目的、終わった作業、検証結果、まだ残っていることを渡して、`complete / verify_more / incomplete` のような判断に使える。

構成としてはこう。

```text
AI Agent
   ↓
作業する
   ↓
「完了しました！」
   ↓
  Jev
   ↓
本当に終わった？
   ↓
complete / verify_more / incomplete
   ↓
必要ならAgentに戻す
```

これ、かなり好き。

**作業するAIと、終わったか疑うAIを分ける。**

AIを信用してない構成。

でも自律化するなら、このくらい疑ってる方が安心できる。

---

## 🔥 使い道その2：PostgreSQLバックアップが50時間止まってる。どうする？

最近実際にあったケースを当てはめてみる。

```text
PostgreSQL Backup

Age:       50h
Threshold: 25h
Status:    stale
App:       running
```

アプリ自体は動いてる。でもバックアップは50時間更新されてない。

さて、どれ？

```text
今すぐ対応
今日中
今週
保留
```

こういう候補をChoiceで判断させる。

さらにScoreで影響度、Noulで「人間へ通知すべき？」も聞く。

### いや、if文でよくない？

その通り。

```ts
if (backupAgeHours > 25) {
  alert();
}
```

これで済むなら絶対こっち。

AIいらない。

ただ、「サービス自体は動いてる」「別の復旧手段がある」「メンテ時間が近い」「同時に別の障害も起きてる」みたいに条件が増えてくると、単純な閾値だけでは決めにくくなる。

**ルールにするにはちょっと曖昧。**

ここにJevを置くのは面白そう。

---

## 🔥 使い道その3：AIが本番DBを触ろうとしてる

これは怖い。

AI Agent：

> 本番DBの古いレコードを削除します

自分：

> 待て。

Jevには `tool-guard` がある。

ツール呼び出しの前に `allow / confirm / review / deny` のような判断を挟める。

```text
AI Agent
    ↓
「DB削除します」
    ↓
Jev Tool Guard
    ↓
allow / confirm / review / deny
          ↓
       必要なら人間確認
```

Jev自身がDBを削除するわけじゃない。

**「これ実行していい？」だけ判断する。**

例えば、READMEを読むならallow、本番DBを変更するならreview、みたいに扱える。

AIエージェントに権限を渡せば渡すほど、この層は欲しくなる。

---

## 🤖 使い道その4：どのAIに投げる？

最近のAIアプリ、モデルが1個とは限らない。

```text
Fast Model
→ 速い・安い

Reasoning Model
→ 重い・高い・強い
```

全部Reasoning Modelに投げたら楽。でも高い。

全部Fast Modelなら安い。でも難しいタスクで困る。

そこで `model-route`。

```text
ユーザーのリクエスト
        ↓
       Jev
        ↓
   どっち使う？
     ┌──┴──┐
   Fast   Reasoning
```

**LLMを呼ぶ前にAIがモデルを選ぶ。**

AIの前にAI。

ちょっと面白い。

複数Provider・複数モデルを使うサービスなら、普通に候補に入りそう。

---

## 🤖 Hertaに入れるなら？

自分で作っているDiscord BotのHertaにも当てはめてみる。

例えばDiscordでイベントが来る。

```text
Discord Event
      ↓
     Jev
      ↓
何をするイベント？
```

そこで、「通常ルールで処理」「Fast LLMへ」「Strong LLMへ」「モデレーター確認」「何もしない」みたいに振り分ける。

```text
Discord Event
     ↓
    Jev
     ↓
 ┌───┼──────────────┐
Rule  Fast LLM  Strong LLM
 │       │          │
 └───────┴──────────┘
          ↓
       Response
```

「とりあえず全部LLMに投げる」より役割が分かりやすい。

公式ユースケースにもIntent Routing、Content Moderation、Invoice Classification、CSV Validation、Claim Verificationなどがある。

つまり、**何かを生成するより「どれ？」「どうする？」が得意な立ち位置。**

Discord Botとは結構相性よさそう。

---

## 🤔 じゃあif文とLLMのどっちなの？

ここまで見て、自分の中ではこう整理した。

```text
ルールが明確
──────────────
if / switch

     ↓

ちょっと曖昧
複数情報から判断したい
──────────────
Jev

     ↓

調査したい
説明してほしい
コードを書いてほしい
──────────────
LLM / Agent
```

例えば `if (age >= 18)` で終わるものをJevには聞かない。

一方で、「障害の深刻度・現在のサービス状態・復旧手段・他のインシデント・人間レビューの必要性を全部見て次の対応を決めて」なら、Jevの出番が見えてくる。

**if文にするには曖昧。LLMに長文を書かせるほどでもない。**

この間。

なるほど、ここか。

---

## ⚠️ Jevが「OK」って言ったから実行！は怖い

例えばJevが高い確率で `allow` を返したとする。

じゃあ本番DB削除！

……とはならない。

怖すぎる。

Jevのドキュメントでも、probabilityはsignalとして扱い、authorizationそのものにはしないよう注意されている。

なので自分ならこうする。

```text
Jev
 ↓
判断
 ↓
アプリ側のルール
 ↓
必要なら人間承認
 ↓
実行
```

特に削除・決済・本番変更・権限変更・個人情報まわりは、AIの判断だけで直接実行させない。

Jevは**決定権者**じゃなくて、**判断材料を返すやつ**くらいがちょうどよさそう。

---

## 🧪 今回は実際には叩いてない

ここ大事。

今回はJevのアカウントを作って、APIを実際に叩くところまではやってない。

なので、「精度めっちゃ高い！」「爆速！」「LLMより絶対いい！」みたいなことは言えない。

公式サイトではミリ秒級の応答などが紹介されているけど、今回は自分で測っていない。

**性能評価はしてない。**

ただ、APIを読んで「何に使うものなのか」はかなりイメージできた。

そして一番気になったのはやっぱりこれ。

```text
AI Agent
   ↓
作業
   ↓
「終わりました！」
   ↓
Jev
   ↓
「本当に終わった？」
```

これ、実際に組んでみたい。

---

## まとめ

最初：

> 判断だけするAI？ 何に使うん？

APIを読む。

```text
completion
tool-guard
model-route
decisions
```

自分：

> あ、AIエージェントの前後に置くやつか。

となった。

個人的に気になったのは、AI Agentの完了チェック、危険なTool Callのガード、Issueや障害のトリアージ、モデルルーティング、Discord Botの判断レイヤーあたり。

何でもLLMに投げるんじゃなくて、

**「これ、生成してほしいのか？ 判断してほしいだけなのか？」**

を分ける。

```text
入力
 ↓
Jev ── 判断
 ↓
LLM / Agent ── 作業
 ↓
Jev ── 本当に終わった？
 ↓
完了
```

この構成、ちょっと試したくなる。

---

## 参考

- Qiita「あなたはもう試した？判断特化AI『Jev』で遊ぼう！」
- Jev API REST Docs
- Jev Use Cases
