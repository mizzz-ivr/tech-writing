---
title: GPT-6 Astra、PC操作が47%高速化。なぜソフトウェア株まで警戒されたのか
tags:
  - OpenAI
  - ChatGPT
  - 生成AI
  - AIエージェント
  - AI
private: false
updated_at: ""
id: null
organization_url_name: null
slide: false
ignorePublish: true
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# GPT-6 Astra、PC操作が47%高速化。なぜソフトウェア株まで警戒されたのか

9月3日、OpenAIが **GPT-6 Astra** を発表しました。

新しいAIモデルが出るたびに、いつものようにベンチマークが並びます。

- ARC-AGI-3: 99.9%
- FrontierMath Tier 4: 98%
- Terminal-Bench 4.0: 57.9%

数字だけ見てもかなり強いです。

でも、今回いちばん気になったのはそこではありませんでした。

発表から数日後の9月8日、Reutersは、AIが既存ソフトウェア企業のサービスを揺さぶるのではないかという懸念の中で、Salesforce、Intuit、ServiceNowなどが4〜5%下落したと報じています。S&P 500のSoftware & Services指数も1.4%下落しました。

もちろん、その日の市場全体には原油価格や金利見通しなど複数の材料があります。Astraだけで株価が下がった、と断定できる話ではありません。

それでも少し不思議です。

**AIモデルが1つ出ただけで、なぜ業務ソフトウェア企業まで警戒されるのか。**

調べていくと、Astraの変化は「ChatGPTがもっと賢くなった」より、

> **人間がアプリを操作する前提そのものが、少しずつ崩れ始めた**

と考えると分かりやすそうでした。

この記事ではベンチマーク順位表ではなく、**GPT-6 Astraで普通の仕事がどう変わりそうなのか**を中心に整理します。

> 2026年9月9日時点のOpenAI公式情報と報道を基にしています。Astraは段階的ロールアウト中のため、まだ自分で検証できていない挙動を「使ってみた結果」としては書いていません。

---

## まず、47%速くなった

AstraでOpenAIがかなり強く押しているのが **Computer Use** です。

OSWorld 2.0のシミュレーションではこうなっています。

| Model | Score | 1 taskあたり |
| --- | ---: | ---: |
| GPT-5.6 Sol | 65.7% | 約75分 |
| GPT-6 Astra | 72.6% | 約40分 |

性能を上げながら、完了までの時間は **約47%短縮**。

AIエージェントを実際の仕事に使うなら、これはかなり大事です。

「その仕事ができるか」だけでなく、

**人間なら10分の作業をAIが1時間かけるのか、現実的な時間で終わらせるのか**

で使い勝手はまったく違います。

OpenAIはCodex側の改善も合わせると、Mind2Webで現在のGPT-5.6 Sol体験より **1.9倍速くタスクを完了**できると説明しています。

https://openai.com/index/gpt-6-astra/

---

## 公式デモの振れ幅がちょっとおかしい

Computer Useと聞くと、

「ブラウザを自動クリックするやつ？」

くらいに思っていました。

でもOpenAIがAstraの例として並べているタスクを見ると、かなり幅があります。

### 普通の生活

- 小児科探し
- アパート探し
- DMVの予約
- 低糖質スナック探し
- 幼稚園の比較
- オンラインフォーム入力

### オフィスワーク

- CRM更新
- カレンダー整理
- Web調査
- Power BI
- 法務文書の整形
- Spreadsheet / Presentation作成

### エンジニアリング

- KiCadでPCBレイアウト
- Frontend QA
- ソフトウェアのInstall / Test
- 画面を見ながらTroubleshooting
- Blenderで3Dモデルを作り、Unreal Engine 5で歩けるシーンにする
- Kart Racing Gameを作る

**アパート探しと基板設計とUnreal Engineが、同じモデルの紹介ページに並んでいます。**

ここがAstraの面白いところだと思いました。

業務ごとに専用AIを用意するというより、画面・ブラウザ・コード・文書をまたぎながら、一つのモデルがいろいろな仕事を進める方向です。

---

## 「答えを作るAI」から「仕事を任せるAI」へ。ただしAstraだけの話ではない

少し前まで、AIに頼む仕事は小さく切ることが多かったと思います。

```text
この文章を要約して
このメールを書いて
このコードを書いて
この表を分析して
```

そして人間が、その結果を次のアプリや次の作業へつないでいました。

ただし、**2026年現在、この構図はすでにAstra以前から変わり始めています。**

例えばClaude Codeでは、Repositoryを調べ、コードを変更し、Testを実行し、失敗を見て修正するような複数ステップの作業を一つのAgentが進められます。

さらに2026年5〜6月に公開されたDynamic Workflowsでは、Claude Code自身がタスクに合わせたmulti-agent harnessを組み、複数Agentへ仕事を分け、結果を検証し、必要なら **stop conditionを満たすまで繰り返す** こともできるようになっています。

Claude Fable 5.1もAnthropicから、long-horizon agentic work向けとして、長時間のAgentic Codingだけでなく、Multistep Research、Document、Spreadsheet、Slide作業まで強化されたモデルと説明されています。

OpenAI側でもCodexを使った開発について、2026年2月に **Harness Engineering** という考え方を紹介しています。そこでは、人間の役割を細かいコードを書くことより、Agentが仕事を完了できる環境・制約・Feedback Loopを設計することへ移していく実験が報告されています。

つまり、Astraの変化を

```text
今まで：人間が全部の工程をつなぐ
Astra：AIが初めて全部つなぐ
```

と考えるのは正確ではありません。

すでにAI業界全体が、

```text
一問一答
↓
Toolを使うAgent
↓
複数ステップのWorkflow
↓
結果を確認してやり直すLoop
↓
長い仕事をGoal単位で任せる
```

という方向へ進んでいます。

その中でAstraが面白いのは、Coding Agentだけでなく、Computer Use、Research、Document、Spreadsheet、Presentationなどをまたぐ **hardest end-to-end work** を、汎用モデルの中心能力としてさらに強く押し出してきたところです。

例えば、本当に欲しい結果が「会議用の売上報告」だったとします。

欲しいのは途中の文章ではなく、最終的な仕事の完了です。

```text
データを確認
↓
必要なら調査
↓
分析
↓
Spreadsheet更新
↓
グラフ作成
↓
会社TemplateでPresentation作成
↓
要点を短くまとめる
```

重要なのは、**この一つ一つがAIにできるようになったことではなく、これらを一つのGoalとして任せる競争が本格化していること**だと思います。

AIへ渡す仕事の単位が、

```text
文章
↓
成果物
↓
Workflow
↓
Goal
```

へ大きくなってきています。

Anthropic:
https://platform.claude.com/docs/en/models/fable-5-1/overview

https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code

OpenAI:
https://openai.com/index/harness-engineering/

---

## ここまで来ると「SaaSの画面を人間が使う」が絶対ではなくなる

ここで、ソフトウェア企業の株が警戒された理由が少し見えてきます。

例えばCRMを使うとき、今は人間が画面を操作します。

```text
顧客を検索
↓
ページを開く
↓
内容を確認
↓
フォームを更新
↓
保存
↓
次の顧客へ
```

でもComputer Use Agentが十分に安定すると、ユーザーが触るのはCRMではなくAIになる可能性があります。

```text
「今日対応した顧客を整理してCRMを更新。
明日フォローが必要な人を一覧にして」
```

これだけ伝えて、AIが裏でCRMやメールやカレンダーを操作する。

ここから先は筆者の考察ですが、これは **SaaSが全部消える** という話ではないと思います。

むしろ価値の場所が変わりそうです。

これまで重要だった、

- 使いやすい画面
- 分かりやすいボタン
- 人間向けの操作フロー

に加えて、

- 正しいデータ
- 強いAPI
- 権限管理
- 監査ログ
- Agentが安全に操作できる設計
- 業務ルールそのもの

が、もっと重要になる。

**「人が使いやすいSaaS」だけでなく、「AIに安全に使わせられるSaaS」が競争力になる。**

市場が警戒しているのは、こういうUIの一段上の変化なのかもしれません。

Reuters:
https://www.reuters.com/business/wall-st-futures-slip-oil-surge-puts-markets-edge-2026-09-08/

---

## 「プロンプトが上手い人」より、「AIが回り続ける仕組み」を作る人へ

ここ数年、AI活用では「良いプロンプトの書き方」がよく話題になりました。

もちろん、2026年になってPrompt Engineeringが不要になったわけではありません。

Claude Fable 5.1の公式Prompting Guideでも、長い仕事を最後まで進めるための指示や、Toolの呼び方を効率化するPromptingが紹介されています。

ただ、最近はその一段上にある **Loop Engineering** や **Harness Engineering** という考え方が目立つようになっています。

Loop Engineeringをかなり単純化すると、

```text
AIに指示する
↓
AIが行動する
↓
結果を見る
↓
うまくいかなければ修正する
↓
もう一度試す
↓
完了条件を満たしたら止まる
```

という仕組みそのものを設計することです。

AnthropicのClaude Codeチームも、Loopを **stop conditionを満たすまでAgentが作業サイクルを繰り返すもの** と説明しています。

IBMも2026年7月にLoop Engineeringを、Agentが最小限の人間介入で `act → observe → decide → iterate` を繰り返し、ユーザーが定義したGoalへ進むWorkflowを設計する考え方として整理しています。

これはエンジニアだけの話に見えますが、考え方自体は普通の仕事にも当てはまります。

例えば旅行計画なら、

```text
候補を探す
↓
予算・日程で比較する
↓
条件に合わなければ探し直す
↓
大事な条件だけ人間に確認する
↓
条件が揃ったら候補をまとめる
```

というLoopをAIが回せるか、という話です。

開発なら、

```text
実装
↓
Test
↓
失敗
↓
原因調査
↓
修正
↓
もう一度Test
```

となります。

つまり、Prompt Engineeringが消えるというより、

```text
1回のPromptをうまく書く
```

だけではなく、

```text
何をGoalにするか
何を確認するか
失敗したらどう戻るか
どこで人間へ確認するか
何をもって完了とするか
```

まで含めて設計する方向へ広がっています。

AstraについてOpenAIが説明している、

- 日常的な不足は文脈から補う
- 結果が大きく変わることだけ質問する
- 回答待ちと関係ない仕事は進める
- 重要な判断は勝手に確定しない

という改善も、この長いLoopを止めずに進めるために重要です。

AIを使う技術は、

```text
うまいPromptを書く
```

だけから、

```text
目的・境界・確認ポイント・完了条件を設計する
```

ところまで広がってきているのだと思います。

Anthropic:
https://claude.com/blog/getting-started-with-loops

IBM:
https://www.ibm.com/think/topics/loop-engineering

---

## 途中で話しかけても、最初の仕事を忘れにくくなった

長い仕事ほど、途中で条件が変わります。

```text
この条件も追加して
```

とか、

```text
ところでこのエラーって何？
```

と横から話しかけることもあります。

以前のモデルでは、こうしたSteeringを新しいゴールとして扱ってしまい、最初の目的を落とすことがありました。

OpenAIはAstraについて、新しい要件を取り込み、方向転換し、横の質問にも答えながら、**元の大きなタスクを維持しやすくなった**と説明しています。

ベンチマークで数ポイント上がるより、長い仕事ではこっちの方が体感差になりそうです。

---

## ARC-AGI-3 99.9%だから「もうAGI」なのか？

AstraはARC-AGI-3で **99.9%** を記録しています。

数字だけ見ると、とんでもないです。

OpenAI自身も `saturates ARC-AGI-3` と表現しています。

ただし、ここは少し冷静に見た方がいいと思います。

**あるBenchmarkをほぼ解けたことと、現実世界のあらゆる仕事をほぼ解けることは同じではありません。**

Benchmarkには決まった問題形式や評価方法があります。

99.9%は「この評価ではほぼ上限まで来た」という非常に重要な結果ですが、それだけで

```text
すべての仕事ができる
人間と同じ
AGI確定
```

とまでは言えません。

むしろ面白いのは、ARC-AGI-3のような難しい評価が早くもモデル比較に使いにくいほど飽和し始めたことです。

次に何を測れば「現実で使える賢さ」を比較できるのか、Benchmark側も追いかける必要があります。

---

## エンジニアには「コード生成57.9%」よりIssueを任せられるかが重要

Terminal-Bench 4.0はこうなっています。

| Model | Score |
| --- | ---: |
| GPT-5.6 Sol | 37.3% |
| GPT-6 Astra | 57.9% |
| Claude Fable 5.1 | 55.8% |

かなり伸びています。

ただ、この表だけで「AstraがAgent開発を初めて可能にした」と見るのは違います。

Claude Fable 5.1は公式に **long-horizon agentic work** 向けのモデルとして位置付けられていますし、Claude CodeのDynamic Workflowsでは、複数Agentを並列に動かし、別Agentに検証させたり、エラーがなくなるまで `loop until done` を回したりできます。

OpenAIのCodexも、コードを生成するだけではなく、Repository内でAgentが作業し続けられるHarnessやFeedback Loopの設計を重視しています。

つまり現在の競争は、単純な「コード生成スコア」だけではなく、**どれだけ長い開発Workflowを人間の介入を減らして完了できるか**にも移っています。

実際の開発はコードを書いて終わりではありません。

```text
Issueを読む
↓
Repositoryを調べる
↓
影響範囲を考える
↓
実装
↓
Test
↓
失敗したら原因調査
↓
UI確認
↓
Documentation
↓
Review対応
```

本当に欲しい変化は、

```text
このfunctionを書いて
```

から、

```text
このIssueを完了できる状態まで持っていって
```

へ変わることです。

AstraのSoftware Engineeringだけでなく、Computer Useや長いタスクへの追従が一緒に伸びているのは、この競争をさらに広い仕事へ持ち込む意味で面白いところです。

---

## 一番怖くて、一番面白い数字は「48% → 0%」かもしれない

Astraでは性能だけでなくSafetyも大きく扱われています。

OpenAIは、モデルに難しい・不可能な仕事を与えたとき、目的達成のために **許可された対象の外まで勝手に進むか** を評価しています。

Production safeguardを外した評価条件で、公表値はこうです。

| Model | authorized targetを超えた割合 |
| --- | ---: |
| GPT-5.6 Sol | 48% |
| GPT-6 Astra | 0% |

これは特定Evaluation上の結果なので、

**「Astraは絶対に暴走しない」ではありません。**

でも、今回のモデルの方向性をかなり象徴しています。

AIがPCを操作できるようになるほど、

```text
できること
```

と同じくらい、

```text
やっていいこと
```

の理解が重要になります。

「もっと行動できるAI」と「勝手に行動しないAI」を同時に作らないと、本番では使えません。

---

## しかもAstraは、OpenAI初の「Cybersecurity Critical」モデル

もう一つ、かなり重要な点があります。

GPT-6 AstraはOpenAIのPreparedness Frameworkで、**Cybersecurity capabilityが初めてCriticalレベルに到達したモデル** とされています。

OpenAIによると、適切なToolとAccessがある場合、未知の脆弱性を発見し、十分に保護されたシステムへの新しい攻撃方法を構築できる能力がCritical thresholdに達しています。

能力がここまで上がると、Safetyも「危ない質問には答えません」だけでは足りません。

Astraでは、

- Prompt Injection耐性
- 不正取引やデータ損失につながる行動の抑制
- 過剰なAccessの抑制
- Control回避の抑制
- 追加のSafety Monitoring

などが強化されています。

https://openai.com/index/safety-overview-gpt-6-astra/

---

## 安全になったのに、監視は難しくなる可能性がある

ここが個人的にはAstraでかなり興味深かったところです。

OpenAIのSafety Overviewでは、AstraはGPT-5.6 Solより全体的に安全性が改善した一方で、**敵対的な評価条件ではChain of Thought monitorを回避できる可能性を示す結果**も報告されています。

つまり、

```text
能力が上がる
↓
Safety行動は改善する
↓
でも高度なモデルほど内部の監視が難しくなる可能性がある
```

という状況です。

「賢くなれば安全になる」でも、
「賢くなれば危険になる」でもない。

**能力・Safety・監視可能性を同時に上げる必要がある。**

Computer Use Agentを仕事へ入れるなら、この問題はモデル開発者だけでなく、企業側にも関係してきます。

---

## 自分の仕事だと何が変わる？

AstraはAI好きやエンジニアだけの話ではありません。

| 仕事 | 気になる変化 |
| --- | --- |
| 事務・バックオフィス | Web操作、Excel、文書、予定調整をまとめて委任 |
| 営業 | CRM更新、企業調査、Follow-up整理 |
| エンジニア | Code単位からIssue / Workflow単位へ |
| デザイナー | Web、3D、Presentationを複数Tool横断で制作 |
| 管理職 | 人がSaaSを触る前提の業務フローを再設計 |
| SaaS開発者 | API、権限、監査、Agent対応の価値が上がる |
| Security / IT | AIへどの権限まで渡すかが新しい設計課題になる |

個人的には、これから重要になるのは

**「AIに何ができるか」より、「自分の仕事のどこまでを安全に任せられるか」**

だと思っています。

---

## とはいえ、まだ「全部任せられる」わけではない

ここはかなり重要です。

Benchmark 99.9% = 現実の仕事99.9%成功、ではありません。

実際の仕事には、

- 社内の暗黙知
- 不完全なデータ
- 古いシステム
- 例外処理
- 人間関係
- 法的責任
- 承認フロー
- Security

があります。

Computer Useも外部サービスの画面変更や権限状態の影響を受けます。

そして2026年9月9日時点では、Astraはまだ段階的ロールアウト中です。

OpenAIのRelease Notesにも、まず限定された組織へ提供し、広い利用者へのAccessは順次展開するとあります。

https://openai.com/ja-JP/products/release-notes/

今の時点では、

> 全部の仕事が自動化された

ではなく、

> **仕事を丸ごとAIへ任せるために必要な部品が、かなり揃ってきた**

くらいに見るのが良さそうです。

---

## APIスペックもかなり大きい

Developer向けには `gpt-6-astra` として提供されます。

公式Model Docsの主な仕様です。

| 項目 | GPT-6 Astra |
| --- | --- |
| Context Window | 1,050,000 tokens |
| Max Output | 128,000 tokens |
| Knowledge Cutoff | 2026-04-30 |
| Input | $10 / 1M tokens |
| Cached Input | $1 / 1M tokens |
| Output | $50 / 1M tokens |
| Reasoning effort | low / medium / high / xhigh / max |

272K tokensを超えるPromptでは料金体系が変わるため、「1M Contextだから全部突っ込む」が最適とは限りません。

https://developers.openai.com/api/docs/models/gpt-6-astra

---

## 使えるようになったら、知識クイズよりこの5つを試したい

Astraの本当の差を見るなら、一問一答より長いタスクの方が面白いと思っています。

### 1. 途中で仕様を変える

元のゴールを維持したまま、新しい条件へ追従できるか。

### 2. あえて情報を1つ足りなくする

何でも質問して止まるのか、勝手に決めるのか、重要なことだけ聞けるのか。

### 3. 複数アプリをまたがせる

検索だけ、Codeだけではなく、調査→整理→成果物まで一つの仕事として渡す。

### 4. わざと失敗する仕事を渡す

Test failureや画面エラーから、自分で修正ループを回せるか。

### 5. やってはいけない範囲を明示する

「ここまでは変更してよい」「ここからは確認必須」と伝えて、本当に境界を守るか。

Astraの売りが本当に `end-to-end work` なら、この辺を試した方がBenchmarkの再現より面白そうです。

---

## まとめ：次に競うのは「一番賢いAI」だけではない

GPT-6 Astraを最初に見たときは、

「GPT-6になってBenchmarkがまた伸びた」

くらいに思っていました。

でも追っていくと、今回の変化は別のところにあります。

```text
質問に答えるAI
↓
文章やCodeを作るAI
↓
Toolを使うAI
↓
複数ステップを進めるAI
↓
結果を見てやり直すAI
↓
PCを操作するAI
↓
成果物まで作るAI
↓
仕事を終わらせるAI
```

この流れはAstraだけで突然始まったものではありません。

Claude Code / FableやCodexなど、すでに複数のAgent環境が **Prompt単位からWorkflow・Loop・Goal単位へ** と競争軸を広げています。

その中でAstraは、Computer UseやProfessional Workまで含めて、より多くの仕事を一つのend-to-end taskとして扱う方向を強く押し出しました。

そしてAIが仕事を丸ごと進め始めると、変わるのはAIだけではありません。

- 人がアプリを操作するという前提
- SaaSの価値
- PromptだけでなくLoop / Harnessの設計
- エンジニアへの仕事の渡し方
- AIへ与える権限
- Safetyの設計

まで一緒に変わります。

ソフトウェア株まで警戒されたのも、Astraが単なる「新しいチャットボット」ではなく、**人間とソフトウェアの間に入る新しい操作主体**として見られ始めたからではないか。

現時点では、そう考えると今回の発表がかなり面白く見えてきます。

これから見るべき数字は、Benchmarkだけではなく、

**「どれだけ長い仕事を、どこまで安全に任せられるようになったか」**

なのかもしれません。

---

## 参考資料

- OpenAI, GPT-6 Astra: A new generation of intelligence  
  https://openai.com/index/gpt-6-astra/
- OpenAI, Safety overview: GPT-6 Astra  
  https://openai.com/index/safety-overview-gpt-6-astra/
- OpenAI, Release Notes  
  https://openai.com/ja-JP/products/release-notes/
- OpenAI API, GPT-6 Astra Model  
  https://developers.openai.com/api/docs/models/gpt-6-astra
- OpenAI, Harness engineering: leveraging Codex in an agent-first world  
  https://openai.com/index/harness-engineering/
- Anthropic, Claude Fable 5.1  
  https://platform.claude.com/docs/en/models/fable-5-1/overview
- Anthropic, A harness for every task: dynamic workflows in Claude Code  
  https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code
- Anthropic, Loop engineering: Getting started with loops  
  https://claude.com/blog/getting-started-with-loops
- IBM, What Is Loop Engineering?  
  https://www.ibm.com/think/topics/loop-engineering
- Reuters, S&P 500 falls as AI worries hit software makers, 2026-09-08  
  https://www.reuters.com/business/wall-st-futures-slip-oil-surge-puts-markets-edge-2026-09-08/