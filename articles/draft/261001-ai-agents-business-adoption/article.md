---
title: AI Agentが主流になる今、結局何者？「仕事を任せるAI」を業務に入れるまで
status: draft
published_at: null
article_type: essay
level: null
topics:
  - ai
  - ai-agent
  - agentic-ai
  - automation
  - business
domains:
  - developer-productivity
  - business-automation
languages: []
technologies:
  - OpenAI Agents SDK
  - Microsoft Agent Framework
  - Amazon Bedrock AgentCore
  - Model Context Protocol
  - Agent2Agent
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

# AI Agentが主流になる今、結局何者？「仕事を任せるAI」を業務に入れるまで

最近、AI関連の発表を追っていると、やたらと **Agent** という言葉が出てきます。

OpenAIにはAgents SDKやAgents APIがある。

MicrosoftにはAgent Frameworkがある。

AWSにはAmazon Bedrock AgentCoreがある。

GoogleはAgent同士をつなぐA2Aを進めている。

MCPも、Agentが外部のToolやDataへ接続するための共通レイヤーとして広がっています。

ここまで来ると、

> AI Agentって、結局何者なんだ？

という疑問が出てきます。

Modelの名前ではない。

特定の製品名でもない。

単なる自動化とも少し違う。

自分なりに調べていくと、AI Agentはかなりシンプルに捉えた方が分かりやすそうでした。

**Goalを渡すと、自分で次の行動を選び、Toolを使い、結果を確認しながら、完了まで仕事を進めるSystem。**

これが、今「AI Agent」と呼ばれているものの中心にあります。

今回はAI Agentそのものを分解しながら、

**なぜ2026年にAgentが主流になりつつあるのか。**

そして、

**実際の業務へ入れるなら、どこから始めればいいのか。**

まで考えてみます。

> 2026年10月2日時点の公式情報をもとにしています。

---

## まず、AI Agentの中身を分解してみる

OpenAIのAgents SDKでは、AgentはModelだけではありません。

Instructions、Tools、Guardrails、Handoffsなどを組み合わせ、そのAgentが何をする存在なのかを定義します。

そしてRuntime側では、Agent Loopが動きます。

かなり単純化するとこうです。

```text
Goal
 ↓
考える
 ↓
次のActionを決める
 ↓
Toolを使う
 ↓
結果を確認する
 ↓
まだ終わっていなければ次へ
 ↓
Done
```

例えば、

> 来週の会議に向けて競合3社の最新情報を調べて、比較表を作って、Notionにまとめて

という仕事を渡したとします。

Agentは、ただ文章を生成するだけではありません。

```text
何を調べるか決める
↓
Web Search
↓
情報を読む
↓
不足を判断
↓
追加で検索
↓
比較する
↓
表を作る
↓
Notionへ保存
↓
保存結果を確認
↓
Done
```

途中で情報が足りなければ、また調べる。

Toolが失敗したら、別の方法を試す。

重要な操作なら、人間へ確認する。

つまりAI Agentの本体は、Model単体ではなく、

```text
Model
+
Goal
+
Tools
+
State
+
Agent Loop
+
Permissions
+
Guardrails
+
Observability
```

の組み合わせです。

**LLMが頭脳なら、Agentは「頭脳が実際に仕事できるようにした実行System」**くらいに考えると分かりやすいと思います。

---

## 一番重要なのは「自分で次の一手を選ぶ」こと

AI Agentらしさが出るのは、ここです。

例えば請求書処理。

普通の自動化なら、

```text
PDFを読む
↓
金額を抽出
↓
DBへ登録
```

のように、あらかじめ手順を決められます。

でも現実の仕事は、こんなに綺麗ではありません。

```text
請求書を読む
↓
発注番号がない
↓
関連メールを探す
↓
発注書を見つける
↓
金額が一致しない
↓
担当者へ確認する
↓
回答を受け取る
↓
登録する
```

最初から最後まで一本道ではない。

**途中の結果によって、次にやることが変わる。**

この部分をModelに任せられるようになったことで、従来のAutomationでは扱いづらかった仕事まで対象に入り始めています。

Agentは「すべて自由に動くAI」というより、

**決められたGoalと権限の中で、次のActionを自分で選べるSystem**

と捉えた方が近いです。

---

## Agentを構成する7つの部品

実装を見ると製品ごとに名前は違いますが、業務Agentを考えると大体この7つに分けられます。

### 1. Goal / Instructions

何を達成するAgentなのか。

例えば、

```text
問い合わせ内容を調査し、
返信案を作成する。
返金・契約変更は実行しない。
```

のように役割と境界を決めます。

### 2. Model

判断する部分。

どのModelを使うかだけでなく、Reasoning量、Latency、Costもここに関係します。

### 3. Tools

Agentが現実世界へ触る手段です。

```text
searchCustomer()
searchDocuments()
readEmail()
createDraft()
updateTicket()
```

Toolがなければ、Agentは考えるだけで終わります。

### 4. State / Memory

今どこまで進んだか。

過去に何を確認したか。

Userや案件に関する長期情報を何まで持つか。

長いTaskほど、State管理が重要になります。

### 5. Agent Loop / Harness

Agentを何度も動かす実行部分です。

OpenAIのAgents SDKでも、Model出力にTool Callがあれば実行し、その結果を返して再度Modelを呼び、停止条件までLoopします。

2026年にはOpenAIやAWSが、このHarness自体をかなり明示的な製品機能として扱うようになっています。

### 6. Permission / Guardrails

何をしてよいのか。

```text
読む → OK
Draftを作る → OK
顧客情報を更新 → Approval
返金 → Approval
User削除 → NG
```

みたいな境界です。

### 7. Observability / Evals

何をしたのか。

なぜ失敗したのか。

どのToolを呼んだのか。

そのAgentは本当に業務で使える精度なのか。

Agentは複数Stepを進むので、最終出力だけ見ても原因が追えません。

TracingとEvaluationまで含めて初めて運用しやすくなります。

---

## Single Agentだけでは終わらない

Agentを見ていると、次に出てくるのが **Multi-Agent** です。

例えば1つのAgentへ、

```text
市場調査
契約書確認
売上分析
資料作成
```

を全部任せることもできます。

でも仕事が大きくなると、それぞれ専門Agentへ分ける設計が出てきます。

```text
Orchestrator Agent
 ├─ Research Agent
 ├─ Data Analysis Agent
 ├─ Legal Review Agent
 └─ Report Agent
```

OpenAI Agents SDKにはHandoffがあります。

Microsoft Agent FrameworkもAgentとWorkflow、Harnessを組み合わせられる設計になっています。

GoogleのA2Aは、異なるAgent同士がTaskを受け渡し、協調するためのProtocolとして進められています。

ここで面白いのは、

**AgentがSoftwareの一機能ではなく、System内の「仕事をする主体」になり始めていること**です。

ただし、最初からMulti-Agentにすればいいわけではありません。

Agentが増えるほど、

```text
誰が責任を持つか
Contextをどう渡すか
同じToolを二重実行しないか
Costがどこまで増えるか
どこで止めるか
```

も難しくなります。

まずSingle Agentで成立するなら、その方がシンプルです。

---

## MCPとA2Aは何をしている？

Agent周辺でよく出てくるのがMCPとA2Aです。

ざっくり整理すると、

```text
Agent
 ↓
MCP
 ↓
Tool / Data / Service
```

と、

```text
Agent A
 ↓
A2A
 ↓
Agent B
```

です。

MCPは、Agentic Workflowが外部のToolやDataへ接続するための共通基盤として進化しています。

2026年7月のSpecificationではStateless Core、Tasks、Authorization強化などが入り、よりProduction向けの構成へ進んでいます。

A2Aは、異なるAgent同士が連携するためのProtocolです。

例えば購買Agentが、

```text
在庫Agentへ確認
↓
Supplier Agentへ見積依頼
↓
Finance Agentへ予算確認
```

のように、別のAgentへ仕事を渡す世界です。

これまでは、

```text
AIごとに専用Integrationを作る
```

必要がありました。

今はAgent Ecosystem側にも共通Protocolが生まれ始めています。

ここも、Agentが一時的な流行ではなく **ひとつのSoftware Architectureになりつつある** と感じる部分です。

---

## なぜ今、AI Agentが主流になり始めたのか

単純にModelが賢くなったから、だけではなさそうです。

少し前のAgentは、

```text
LLM
+
Function Calling
+
自前Loop
```

をかなり自分で組む必要がありました。

2026年現在は、

```text
Agent Runtime
Sandbox
Memory
Identity
MCP
A2A
Tracing
Evals
Human Approval
Long-running Task
```

まで周辺Infrastructureが揃い始めています。

OpenAIはAgents SDKを、長時間TaskやSandboxを扱える方向へ進化させています。

AWS AgentCoreにもManaged Harnessが入り、Reasoning、Tool Selection、Action Execution、StreamingまでHarness側が扱えるようになっています。

Microsoft Agent Frameworkも、Tool、Session、Memory、Workflow、Harness、Hostingまで段階的に構築できる構成です。

つまり今起きているのは、

**「Agentが作れるようになった」から「Agentを運用できるようになってきた」への変化**

なのだと思います。

---

## じゃあ、会社のどの仕事をAgentにする？

ここが一番重要です。

「AI Agentを導入する」と決めてから業務を探すと、かなり危ない。

先に見るべきなのは、日々の業務です。

Agentと相性が良さそうなのは、例えばこんな仕事です。

| 業務 | Agentが向いている理由 |
| --- | --- |
| 問い合わせ一次対応 | 内容ごとに調べる情報と判断が変わる |
| 営業リサーチ | Web / CRM / Mailなど複数Sourceをまたぐ |
| 社内ITサポート | 状況確認 → Runbook検索 → 対処の分岐が多い |
| 開発 | Repository調査 → 実装 → Test → ReviewまでLoopできる |
| 障害調査 | LogやMetricを見ながら仮説を更新する |
| 契約・申請確認 | Documentを読み、条件不足なら追加確認できる |
| 採用一次整理 | 複数資料を読み、決められた基準で整理する |

共通しているのは、

```text
入力が毎回少し違う
↓
複数の情報源を見る
↓
途中で判断する
↓
次のActionが変わる
```

という仕事です。

逆に、

```text
Input
↓
決まった処理
↓
Output
```

で済むなら、普通のProgramやWorkflowの方が良いことも多いです。

---

## 業務導入は「AIに何をさせるか」より「どこまで任せるか」

例えば、問い合わせ対応Agentを作るとします。

最終形だけ考えると、

```text
問い合わせ受信
↓
調査
↓
判断
↓
返信
↓
返金
↓
Ticket Close
```

まで全部やらせたくなります。

でも最初からここへ行く必要はありません。

自分なら、4段階に分けます。

### Phase 1 — Read

```text
Mailを読む
Knowledge Baseを検索
顧客情報を確認
過去Ticketを読む
```

まだ何も変更しない。

### Phase 2 — Draft

```text
返信案を作る
対応案を作る
更新内容を提案する
```

人間が確認して実行します。

### Phase 3 — Approval付きAction

```text
AgentがActionを準備
↓
Human Approval
↓
実行
```

ここで初めて実Systemへ書き込みます。

### Phase 4 — Bounded Autonomy

十分に安定した一部だけ自律化します。

例えば、

```text
低RiskなTicket分類
定型的なStatus更新
決められた条件のReminder送信
```

など。

**Agentの導入成熟度は、賢さではなく「安全に渡せる権限の範囲」で考えた方が分かりやすい。**

---

## Agent用の「業務設計図」を先に作る

Platformを選ぶ前に、業務を1枚に分解した方がよさそうです。

例えば、

```text
Goal
問い合わせを解決できる状態へ持っていく

Input
問い合わせ本文

Data
CRM
Knowledge Base
過去Ticket
契約情報

Tools
searchCustomer
searchKnowledge
createDraft
updateTicket

判断
どの情報を調べるか
回答できるか
Escalationが必要か

Approval
返金
契約変更
顧客への最終送信

Done
返信案完成
根拠確認済み
必要なEscalation先を設定済み
```

ここまで書くと、

> Agentに何を実装する？

より、

> どこをAgentへ渡して、どこをSystemや人間に残す？

が見えてきます。

AI Agent導入は、AI機能追加というより **業務Processの再設計** に近いと思います。

---

## Tool設計がAgentの能力を決める

強いModelを使っても、Toolが雑だと業務Agentは扱いづらい。

例えば、

```text
adminExecute(command)
```

みたいな万能Toolを渡すより、

```text
findCustomer()
readContract()
createRefundProposal()
requestRefundApproval()
executeApprovedRefund()
```

のように分けた方が、何をしてよいか管理できます。

ここで重要なのは、

**Toolを便利にすることと、Agentへ権限を渡しすぎないことを両立すること。**

特に書き込み系Actionは、

```text
Read
Draft
Propose
Approve
Execute
```

を分けると扱いやすい。

AgentのPermission設計は、PromptではなくToolとIdentity側でも止める必要があります。

---

## Human-in-the-loopは「保険」ではなくArchitecture

Agent導入でよく聞くHuman-in-the-loop。

単に、

> AIが不安だから人間が最後に確認する

だけだと、運用が曖昧です。

重要なのは、

**どのActionで必ず止めるかを定義すること。**

例えば、

```text
検索 → 自動
要約 → 自動
Draft作成 → 自動
Ticket更新 → 条件付き自動
顧客への送信 → Approval
返金 → Approval
契約変更 → Approval
User削除 → 禁止
```

のようにします。

OpenAIのAgents SDKでも、Tool ApprovalによってRunをPauseし、Approve / Reject後に再開する仕組みがあります。

Agentが強くなるほど、人間をLoopから消すのではなく、

**人間をどこに残すかを明確にする**

設計が重要になります。

---

## 「完了条件」がないAgentはずっと働けてしまう

AgentにはGoalを与えます。

でもGoalだけでは少し足りない。

例えば、

> 障害を調査して

だけだと、どこまでやれば終わりなのか曖昧です。

そこでDoneを決めます。

```text
Goal:
障害原因を調査する

Done:
- 関連Logを確認
- Metricを確認
- 原因候補を3つ以内に絞る
- 根拠を添える
- Production変更はしない
- 不明ならEscalationする
```

開発Agentなら、

```text
Done:
- Test PASS
- Type Check PASS
- Secretなし
- Draft PR作成
- Production Deployしない
```

のようにできます。

**Agentに「どうやるか」を任せるほど、「何をもって終わりか」は人間が明確にする。**

ここがかなり重要です。

---

## Agentを本番へ入れるならTraceが必要になる

Agentは1回Modelを呼んで終わりではありません。

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
Approval
↓
Tool D
↓
Done
```

と進みます。

最終結果だけ見ても、

> なんでこのActionをした？

が分かりません。

だからAgentにはTracingが必要です。

最低でも、

```text
誰の依頼か
どのAgentか
どのModelか
どのToolを呼んだか
Tool引数
Tool結果
Approval履歴
Error
Token / Cost
最終結果
```

を追えるようにしたい。

OpenAI Agents SDKはTracingを提供しています。

AWS AgentCoreもObservabilityをAgent Runtimeの主要機能として扱っています。

AgentのLogは、普通のDebug Logより **Audit Logに近い役割**を持ち始めます。

---

## Evalsなしで「使えそう」は危ない

AgentはDemoだとかなり強く見えます。

でも業務で重要なのは、

> 一度成功した

ではありません。

例えばSupport Agentなら、

```text
Task成功率
人間の修正率
Approval Reject率
Escalation率
誤Tool Call率
平均処理時間
1件あたりCost
```

を見る。

Coding Agentなら、

```text
Test PASS率
Review修正量
Rollback率
Issue完了率
人間介入回数
```

を見る。

Anthropicも2026年のAgent Evalsに関する解説で、Agentは複数TurnでToolを使い、Stateを変えながら適応するため、通常のLLM Outputより評価が難しくなると整理しています。

Agentを本番に入れるなら、

**Promptを書く → 動かす**

ではなく、

**Task Setを作る → Traceを見る → Evalsする → 改善する**

までが開発Loopになります。

---

## 最初からMulti-Agentにしない

Agentという言葉を追っていると、

> 複数Agentが自律的に協力する

世界にすぐ行きたくなります。

確かに面白い。

でもSingle Agentで済むなら、まずそれでいいと思っています。

```text
1 Agent
+
5 Tools
```

で済む仕事を、

```text
Planner Agent
Research Agent
Reviewer Agent
Executor Agent
```

に分けると、途端に、

```text
Context共有
Agent間通信
責任境界
再試行
重複実行
Cost
Trace
```

まで考える必要があります。

Multi-Agentは「Agentの上位版」というより、

**1つのAgentでは役割分離した方がSystem全体を理解しやすいときのArchitecture**

として使う方が自然そうです。

---

## 自分なら、業務導入をこの順番で進める

AI Agentを仕事へ入れるなら、今のところ自分はこの順番が一番しっくりきます。

### Step 1 — Agent化したい「業務」を1つ選ぶ

製品を選ばない。

まず仕事を選ぶ。

### Step 2 — Goal / Input / Data / Tools / Doneを書く

今、人間が何を見て、何を判断しているかを分解します。

### Step 3 — ToolをRead-onlyでつなぐ

最初は検索と参照だけ。

### Step 4 — TraceとEvalsを作る

本番Actionを許す前に、判断の癖と失敗パターンを見る。

### Step 5 — Draftまで任せる

返信案、更新案、PR案などを作らせます。

### Step 6 — Approval付きActionを許す

Side Effectのある処理を限定して開放します。

### Step 7 — 安定した部分だけAutonomousにする

Riskが小さく、成功条件が明確な処理だけ。

### Step 8 — 必要になって初めてMulti-Agent化する

Role分割が本当に必要な部分だけ分けます。

この順番なら、

```text
会社にAI Agentを導入する
```

という大きすぎる話ではなく、

```text
この業務の、この判断とActionをAgentに渡す
```

という小さい変更から始められます。

---

## AI Agentは「AI社員」より「新しい実行主体」と考えたい

AI Agentを説明するとき、

> AI社員

という言葉はかなり分かりやすいです。

ただ、System設計として考えると少し危ない気もします。

人間の社員なら、

```text
空気を読む
暗黙知を理解する
責任を取る
例外に気づく
倫理的判断をする
```

ことまで期待します。

Agentに同じものを期待すると、境界が曖昧になります。

自分はむしろ、

**APIでもCronでも人間でもない、新しい実行主体**

くらいに考えています。

```text
人間
 ├─ 判断
 ├─ 承認
 └─ 責任

Agent
 ├─ 調査
 ├─ 推論
 ├─ Tool Use
 ├─ Loop
 └─ 限定されたAction

System
 ├─ Permission
 ├─ Validation
 ├─ Audit
 └─ Hard Guardrail
```

この3つをどう分けるか。

そこがAgent時代のSystem Designになっていくのかもしれません。

---

## まとめ：AI Agentの主役は「自律性」ではなく「任せられる仕事」

AI Agentを追い始めると、

```text
自律型
Multi-Agent
Computer Use
MCP
A2A
Memory
Planning
Reasoning
```

と新しい言葉が大量に出てきます。

でも中心にあるものは、そこまで複雑ではありません。

```text
Goalを受け取る
↓
状況を見る
↓
次のActionを決める
↓
Toolを使う
↓
結果を見る
↓
必要ならやり直す
↓
Doneまで進む
```

これがAgentです。

そしてAI Agentが主流になるほど、Modelの性能だけでなく、

```text
何を任せるか
何を見せるか
どのToolを渡すか
何を許可するか
どこで人間へ戻すか
何をもって完了とするか
どう評価するか
```

が重要になります。

2026年は、Agentを作るためのRuntime、Protocol、Sandbox、Memory、Observabilityまで揃い始めました。

だから次に考えるべきなのは、

> AI Agentを使うかどうか

より、

**自分たちの仕事の中で、どの仕事をAgentへ渡せる形に設計し直すか**

なのだと思います。

AI Agentは、単にAIが賢くなった話ではない。

**Softwareの中に「自分で仕事を進める主体」が増える話です。**

そこまで考えると、Agentが主流になっていくという言葉の意味が、少し見えやすくなりました。

---

## 参考資料

- OpenAI, Agents  
  https://developers.openai.com/api/docs/guides/agents
- OpenAI, Agents SDK  
  https://developers.openai.com/api/docs/guides/agents/sdk
- OpenAI, Running agents  
  https://developers.openai.com/api/docs/guides/agents/running-agents
- OpenAI, The next evolution of the Agents SDK  
  https://openai.com/index/the-next-evolution-of-the-agents-sdk/
- Anthropic, Building Effective AI Agents  
  https://resources.anthropic.com/building-effective-ai-agents
- Anthropic, Demystifying evals for AI agents  
  https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Microsoft, Agent Framework  
  https://learn.microsoft.com/en-us/agent-framework/get-started/
- Google Developers Blog, How A2A is Building a World of Collaborative Agents  
  https://developers.googleblog.com/how-a2a-is-building-a-world-of-collaborative-agents/
- Google Developers Blog, Developer’s Guide to AI Agent Protocols  
  https://developers.googleblog.com/en/developers-guide-to-ai-agent-protocols/
- Model Context Protocol, The 2026-07-28 Specification  
  https://blog.modelcontextprotocol.io/posts/2026-07-28/
- AWS, Amazon Bedrock AgentCore adds new features to help developers build agents faster  
  https://aws.amazon.com/about-aws/whats-new/2026/04/agentcore-new-features-to-build-agents-faster/
