---
title: 「PR作ってNotionも更新して」で気づいた。AI Agentって結局何者？業務導入の始め方を考える
status: draft
published_at: null
article_type: essay
level: null
topics:
  - ai
  - ai-agent
  - automation
  - business
domains:
  - developer-productivity
  - business-automation
languages: []
technologies:
  - OpenAI Agents SDK
  - Microsoft Agent Framework
  - Model Context Protocol
portfolio_signals:
  - architecture
  - security
  - automation
source_repositories:
  - mizzz-ivr/tech-writing
published:
  qiita: null
  zenn: null
---

# 「PR作ってNotionも更新して」で気づいた。AI Agentって結局何者？業務導入の始め方を考える

最近、AIへの頼み方が少し変わってきました。

以前なら、

> 次のQiita記事の構成を考えて

くらいで終わっていたところを、今は、

> Repositoryを見て既存記事と被っていないか確認して、必要なことを調べて、原稿を書いて、GitHubにPRを作って、Notionにも進捗を残して

みたいに頼むことがあります。

文章を書くだけではありません。

Repositoryを読む。

既存記事を確認する。

Webで調べる。

原稿を書く。

GitHubを操作する。

Notionを更新する。

必要なら結果をもう一度確認する。

こうして並べると、もう「質問に答えるAI」ではありません。

**ひとつのGoalに向かって、複数のToolを使いながら仕事を進めるAI**です。

そこで改めて気になりました。

**AI Agentって、結局何者なんだろう。**

2026年に入ってから、OpenAI Agents、Microsoft Agent Framework、Amazon Bedrock AgentCore、GoogleのA2A、MCPなど、周辺の仕組みまで一気に揃ってきました。

ただ、業務へ入れることを考えると、

> Agentを導入しよう

だけではかなり危ない気がします。

今回は、AI Agentを「すごいAI社員」のようなイメージではなく、**業務システムとしてどう捉えると分かりやすいか**を、自分なりに整理してみます。

> 2026年10月1日時点の公式情報をもとにしています。

---

## ChatbotとAgent、何が違う？

普通のLLM呼び出しをかなり単純化すると、こうです。

```text
User
  ↓
Prompt
  ↓
Model
  ↓
Answer
```

質問を渡して、答えを受け取る。

Tool Callingが入る場合でも、アプリ側が「この関数を呼ばせる」とかなり固定的に組めます。

一方、Agentはもう少しLoopに近い。

```text
Goal
  ↓
Modelが次の行動を判断
  ↓
Toolを使う
  ↓
結果を観測
  ↓
次の行動を判断
  ↓
必要ならまたToolを使う
  ↓
完了 / Human Approval / Stop
```

OpenAIのAgents SDKでも、AgentはModel、Instructions、Tools、Guardrails、Handoffsなどをまとめた単位として扱われています。

そしてRunnerは、

```text
Modelを呼ぶ
↓
Tool Callがあれば実行
↓
結果をModelへ戻す
↓
必要なら繰り返す
↓
Final Answerで終了
```

というAgent Loopを回します。

Anthropicも、Agentを

> 自分でProcessとTool Useを決めながらTaskを進めるAI

として説明していて、実際の動きは

```text
plan
→ act
→ observe
→ adjust
→ repeat
```

に近いです。

ここまで見ると、自分の中ではかなり整理しやすくなりました。

**Agentは「すごく賢いChatbot」というより、LLMを判断部分に使った実行Loopです。**

Modelの賢さだけで決まるものではありません。

どんなToolを渡すか。

何を許可するか。

どこで止めるか。

何をもって完了とするか。

その外側の設計まで含めてAgentです。

---

## WorkflowとAgentも、同じではなかった

ここも最初はかなり混同していました。

例えば請求書処理が、

```text
PDFを読む
↓
項目を抽出
↓
金額を検証
↓
会計システムへ登録
```

と毎回同じ順番なら、普通のWorkflowで十分です。

コードで順番を決めればいい。

でも実際には、

```text
PDFの内容が足りない
↓
関連メールを探す
↓
発注情報と照合する
↓
まだ足りなければ人間へ確認
↓
揃ったら登録
```

のように、状況によって次の行動が変わることがあります。

この「次に何をするか」をModel側へある程度任せると、Agentらしくなってきます。

Anthropicはこの違いをかなり明確にしていて、

- Workflow: あらかじめ定義したCode PathでLLMとToolを動かす
- Agent: LLM自身がProcessとTool Useを動的に決める

と整理しています。

Microsoft Agent FrameworkのDocumentationにも、かなり分かりやすい一文があります。

> If you can write a function to handle the task, do that instead of using an AI agent.

これ、かなり重要だと思いました。

**AgentにできるからAgentにする、ではない。**

普通のFunctionやWorkflowで書けるものを、わざわざ確率的なModel判断へ渡す必要はありません。

---

## それでも、なぜ今こんなにAgentなのか

Agentという考え方自体は急に生まれたわけではありません。

ただ、2026年現在は「試作品を作るための部品」だけではなく、Productionへ持っていく周辺機能がかなり増えています。

OpenAIにはAgents SDKがあり、Tool、Handoff、Guardrail、Tracing、Human Reviewを組めます。

Microsoft Agent Frameworkには、Agent、Workflow、Memory、Middleware、MCP、Human-in-the-loop、長いTask向けのAgent Harnessがあります。

AWSにはAmazon Bedrock AgentCoreがあり、RuntimeだけでなくMemory、Gateway、Identity、ObservabilityまでAgent向けに分けて扱えるようになっています。

Googleは異なるAgent同士をつなぐA2Aを公開しました。

MCPも、Modelへ外部ToolやDataをつなぐ共通層として広がり、2026年7月のSpecificationではStateless Core、Tasks、Authorization強化などが追加されています。

少し前なら、

```text
LLM
+
Function Calling
+
自前のLoop
```

をかなり自分で組む必要がありました。

今は、

```text
Model
Tool
Memory
Identity
Approval
Tracing
Evaluation
Protocol
Runtime
```

のように、Agentを運用するための部品自体がひとつのSoftware Stackになっています。

だから「AI Agentが急に賢くなった」だけではなく、**Agentを業務システムとして扱うためのInfrastructureが揃ってきた**ことも大きいのだと思います。

---

## では、会社で何からAgent化する？

ここで一番やりたくなるのが、

> 面倒な業務を丸ごとAgentに任せよう

です。

でも、自分なら最初からそこには行きません。

例えばカスタマーサポートを考えます。

いきなり、

```text
問い合わせ受信
↓
Agentが判断
↓
返金
↓
メール送信
↓
Ticket Close
```

まで自動化するのは怖い。

返金条件を誤認したら実害が出ます。

送ったメールは取り消せないかもしれません。

そこで、最初はこうします。

```text
問い合わせ受信
↓
関連情報を検索
↓
返信案を作る
↓
根拠を添える
↓
Human Review
↓
人間が送信
```

この状態でも、十分にAgentです。

Agentが自分でKnowledge Baseや顧客情報を調べ、必要なToolを選び、返信案まで作る。

ただし、**Side Effectの最後だけ人間が持つ。**

これなら、Agentの価値を試しながらBlast Radiusをかなり小さくできます。

---

## 自分なら、4段階で権限を広げる

業務導入を考えるとき、機能より先に「どこまで行動してよいか」で段階を分けると分かりやすそうです。

| 段階 | Agentに任せること | 例 |
| --- | --- | --- |
| 1. Read-only | 読む・検索する・整理する | Mail / Docs / DBを調べて要約 |
| 2. Draft | 変更案を作る | 返信案、PR案、Ticket案を作成 |
| 3. Approval付きWrite | 実行直前で人間が承認 | PR作成、Calendar変更、CRM更新 |
| 4. Bounded Autonomy | 明確な範囲内だけ自律実行 | 特定条件のTicket分類、限定された自動更新 |

いきなりLevel 4から始めなくてもいい。

むしろ最初は、

**Agentがどれだけ正しく判断できるかを見るより、間違えたときにどこまで被害を限定できるかを見る。**

この方が業務システムとして考えやすいです。

---

## Promptより先にPermissionを設計したい

Agent導入で一番怖いのは、Modelが間違った答えを返すことだけではありません。

**間違った判断のままToolを実行できること**です。

例えば、

```text
「不要なUserを整理して」
```

という依頼を受けたAgentが、

```text
listUsers()
↓
判断
↓
deleteUser()
```

までできるとします。

Promptをどれだけ丁寧に書いても、ここに絶対はありません。

自分ならTool側で分けます。

```text
listUsers
getUser
getLastLogin
proposeUserDeletion

ここまではAgent
-------------------------
deleteUser

ここからはApproval必須
```

OpenAIのAgents SDKでも、Side Effectを伴う操作ではHuman ReviewでRunをPauseし、Approve / Rejectしてから同じStateをResumeできるようになっています。

重要なのは、Human-in-the-loopを

> AIが不安だから最後に人が見る

という曖昧な仕組みにしないことです。

**どのTool Callで止めるかをSystemとして決める。**

ここまでやって初めて、業務へ入れやすくなります。

---

## Agentに「管理者権限」は渡したくない

人間のAccountで考えると普通なのに、AIになると忘れそうになるのがLeast Privilegeです。

例えばGitHubを操作するAgentなら、

```text
Repository Read
Issue Write
Pull Request Write
```

は必要かもしれません。

でも、

```text
Organization Admin
Secret Read
Repository Delete
```

まで渡す理由はありません。

Agent専用Identityを作り、Roleを分け、ToolごとにScopeを限定する。

これはAI特有の話というより、普通のSecurity設計です。

AWSがAgentCoreでIdentityを独立したResourceとして扱っているのも、Agentが外部SystemへアクセスするほどIdentity設計が重要になるからだと理解しています。

**AIだから特別な権限モデルが必要というより、AIも普通のWorkloadとして扱う。**

この考え方が一番安全そうです。

---

## 「終わった」を誰が決める？

もう一つ、Agentを作ると意外と難しいのがCompletion Criteriaです。

人間へ、

> このIssue直しておいて

と言えば、

- Codeを直す
- Testする
- Lintする
- PRを書く
- Review指摘を直す

あたりまで暗黙に想像できます。

Agentは、どこを「完了」とするかをSystem側でかなり明示した方がいい。

例えば、

```text
Goal:
Issue #123を修正する

Done:
- Unit Test PASS
- Type Check PASS
- Security Scan PASS
- DiffにSecretなし
- PRをDraftで作成
- 本番Deployはしない
```

くらいまで決める。

Agentの能力が上がるほど、Promptを細かくする必要がなくなる部分もあります。

一方で、**Goal / Constraint / Completion Criteriaはむしろ重要になる**と思っています。

「どうやるか」はAgentに任せても、

「何をもって成功とするか」は人間側に残る。

ここはかなり大きな境界です。

---

## Agentは、動いたかではなくTraceを見たい

普通のAPIなら、

```text
Request
↓
Response
```

を見ればかなり追えます。

Agentは違います。

```text
Model
↓
Tool A
↓
Model
↓
Tool B
↓
失敗
↓
Tool C
↓
Model
↓
Human Approval
↓
Tool D
↓
完了
```

と途中経路が長い。

最終結果だけ見ると、

> なぜこんな操作をした？

が分からなくなります。

OpenAIはAgents SDKでTracingを提供しています。

AWS AgentCore Observabilityも、Session、Latency、Token Usage、Error、Traceなどを確認できるようにしています。

Agentを業務へ入れるなら、最低でも、

```text
誰の依頼か
どのAgentか
どのModelか
どのToolを呼んだか
引数は何だったか
結果はどうだったか
Human Approvalはあったか
最終的に成功したか
```

は追えるようにしたい。

**AgentのLogはDebug用ではなく、Audit Logに近くなっていく。**

そう考えると、Production AgentでObservabilityが大きな機能になっているのも納得できます。

---

## 「便利そう」ではなく、成功条件を数字にする

AI AgentのDemoはかなり面白いです。

ブラウザを操作する。

資料を作る。

Codeを直す。

複数Agentが相談する。

見ているだけで、何でもできそうに感じます。

でも業務導入で知りたいのは、

> Demoで成功したか

ではありません。

例えば問い合わせ返信Agentなら、

```text
自動生成率
人間の修正率
承認Reject率
誤ったTool Call率
平均処理時間
1件あたりCost
Escalation率
```

を見たい。

Code Agentなら、

```text
Test PASS率
Reviewでの修正量
Rollback率
Issue完了までのLead Time
人間が途中介入した回数
```

が見たい。

Agentは非決定的なので、

> 一回うまくいった

では弱い。

**繰り返しTaskを流して、どの失敗がどれくらい起きるかを見る。**

このEvaluationまで含めて導入だと思います。

---

## 実は「Agentを使わない判断」もかなり重要

ここまでAgentの話を書いてきましたが、何でもAgent化するのは違うと思っています。

例えば、

```text
CSVを受け取る
↓
ColumnをValidation
↓
DBへINSERT
```

のように処理が完全に決まっているなら、普通のProgramの方が速くて安くて予測しやすい。

Agentを入れる価値が出やすいのは、

```text
入力が毎回少し違う
必要な情報源が変わる
途中結果を見て次の行動を変える
例外が多い
人間が今まで判断していた
```

ようなところです。

逆に、

```text
同じInputなら必ず同じOutputが必要
1ms単位のLatencyが重要
失敗が許されない
実行手順を完全にCodeで書ける
```

なら、Agentにしない方が自然です。

AI Agentの導入判断は、

> どこをAIに置き換えるか

ではなく、

> **どの判断をModelに渡すと、System全体がシンプルになるか**

で考えた方が良さそうです。

---

## GitHubとNotionをまたぐ作業で、ちょうど腑に落ちた

最初の話に戻ります。

記事を書くとき、

```text
Repositoryを読む
↓
既存記事との重複を見る
↓
公式Sourceを調べる
↓
原稿を書く
↓
Branchを切る
↓
PRを作る
↓
Notionへ進捗を記録
```

という作業をひとつのGoalとしてAIへ渡せるようになってきました。

ここで価値があるのは、文章生成だけではありません。

途中で、

> このRepositoryではDraftをどこへ置く？

を確認し、

> 既存記事と主題が被っていない？

を判断し、

> PRはDraftにする？

まで状況に合わせて次のActionを変えられることです。

一方、公開ボタンや本番Deployまで勝手に進めてほしいわけではありません。

自分にとって欲しいのは、

**何でもできるAgentではなく、任せた範囲の中では自分で進み、境界に来たら止まれるAgent**です。

この感覚が、業務導入でもかなり近い気がします。

---

## 自分なら、業務Agentはこう始める

最初にやるのは、Agent Platformを選ぶことではありません。

まず1つ、繰り返している業務を選びます。

そして、その業務を

```text
Input
↓
判断
↓
参照するData
↓
使うTool
↓
Side Effect
↓
Approval
↓
Done
```

に分けます。

次に、Side Effectを外してRead-onlyで動かします。

安定してきたらDraftを作らせる。

その次にApproval付きでWriteを許可する。

それでも安定している一部だけ、自律実行へ広げる。

この順番なら、

```text
AIを導入する
```

という大きなProjectではなく、

```text
この1業務の、この判断だけをAgentへ渡す
```

という小さい変更から始められます。

個人的には、こっちの方が現実的です。

---

## まとめ：Agentの正体は「自律性を持ったLoop」

AI Agentについて調べる前は、

> LLMがもっと賢くなったもの

くらいの感覚がありました。

でも今は少し違います。

```text
Model
+
Instructions
+
Tools
+
State
+
Loop
+
Permissions
+
Approval
+
Observability
+
Evaluation
```

これ全体がAgentです。

そして業務で一番難しいのは、Modelを選ぶことではなく、

**どこまで自律させるかを決めること**だと思っています。

AI Agentが主流になっていくほど、

> 何ができる？

より、

> 何をしていい？
> どこで止まる？
> 失敗したらどう戻す？
> 何をもって完了？
> あとから追跡できる？

の方が重要になる。

だから最初から「AI社員」を作ろうとしなくていい。

まずは、

**読める。調べられる。案を作れる。でも勝手には確定しない。**

くらいから始める。

その境界を少しずつ広げていく方が、Agentを業務へ自然に入れられる気がしています。

そして数年後、Agentが本当に当たり前になったとしても、最後まで残る設計はたぶん同じです。

**自律性には、必ず境界が必要です。**

---

## 参考資料

- OpenAI, Agents SDK  
  https://developers.openai.com/api/docs/guides/agents/sdk
- OpenAI, Running agents  
  https://developers.openai.com/api/docs/guides/agents/running-agents
- OpenAI, Guardrails and human review  
  https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
- Anthropic, Trustworthy agents in practice  
  https://www.anthropic.com/research/trustworthy-agents
- Anthropic, Building effective agents  
  https://www.anthropic.com/engineering/building-effective-agents
- Microsoft, Agent Framework Overview  
  https://learn.microsoft.com/en-us/agent-framework/overview/
- Google Developers Blog, Announcing the Agent2Agent Protocol (A2A)  
  https://developers.googleblog.com/a2a-a-new-era-of-agent-interoperability/
- Model Context Protocol, The 2026-07-28 Specification  
  https://blog.modelcontextprotocol.io/posts/2026-07-28/
- AWS, Amazon Bedrock AgentCore Observability  
  https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html
