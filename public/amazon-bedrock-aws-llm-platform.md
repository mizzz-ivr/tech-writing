---
title: AWSを開いたらGPT-6もClaudeもいた。Amazon Bedrockって結局何者？
tags:
  - AWS
  - AmazonBedrock
  - OpenAI
  - Claude
  - 生成AI
private: false
updated_at: ""
id: null
organization_url_name: null
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---

## 結論

2026年9月22日。

AWSを見る。

> OpenAI GPT-6 Sol / Luna が Amazon Bedrock で一般提供開始

「お、GPT-6もBedrockに来たのか」

と思った。

そして9月28日。

またAWSを見る。

> Claude Sonnet 5.5 がAWSで利用可能に

……。

**AWS、AIモデル集めすぎでは？**

しかもBedrockのモデル一覧を見ると、Amazon Novaだけではない。

Claudeがいる。

GPTがいる。

DeepSeekもいる。

Kimiもいる。

xAIもいる。

Amazon Bedrockの公式ドキュメントでは、現在100を超えるFoundation Modelを扱っている。

自分は少し前まで、

> Amazon Bedrock = AWSからClaudeとかを呼ぶためのLLM API

くらいに思っていた。

でも今のBedrockを見ると、その説明だとかなり足りない。

むしろ、

**「モデルを選ぶサービス」ではなく、「モデルが変わってもAIアプリの運用基盤をなるべく変えないための場所」**

に見えてきた。

今回は、

> GPT-6までBedrockにいるけど、そもそもBedrockって何者なんだ？

というところから、今のAmazon Bedrockを見直してみる。

---

## 1週間でGPT-6とClaudeの新モデルがAWSに来た

まず最近の動きがかなり面白い。

2026年9月22日、AWSはOpenAIの **GPT-6 Sol / GPT-6 Luna** をAmazon Bedrockで一般提供開始した。

その6日後の9月28日には、Anthropicの **Claude Sonnet 5.5** がAWSで利用可能になった。

数年前なら、

```text
OpenAIを使う
→ OpenAIのAPI

Claudeを使う
→ AnthropicのAPI
```

と考えるのがかなり自然だった。

今はAWSを開くと、

```text
Amazon Bedrock
├─ Amazon Nova
├─ Anthropic Claude
├─ OpenAI GPT
├─ DeepSeek
├─ Moonshot AI / Kimi
├─ xAI
└─ ...
```

みたいな世界になっている。

**AWSなのに、Amazon製モデルだけの場所ではない。**

ここがまず面白い。

最初は「AWS版のLLM API」と思っていたけど、それよりAIモデルのセレクトショップに近い。

ただし、Bedrockの価値は「モデルがいっぱい並んでいる」だけではなかった。

---

## Claudeにいたっては「AWSで2通り」になった

今回さらに面白かったのがClaude Sonnet 5.5。

AWSの発表では、Claude Sonnet 5.5へアクセスする方法として、

- Amazon Bedrock
- Claude Platform on AWS

の2つが案内されている。

最初にこれを見たとき、

> え、AWSの中にClaudeが2つあるの？

となった。

でも、この2つの違いを見るとBedrockの立ち位置がかなり分かりやすい。

### Claude Platform on AWS

AnthropicのネイティブなPlatform体験をAWS上で使う方向。

Anthropic側のAPIや機能、Console体験を使いたいときはこちらが自然。

### Amazon Bedrock

Claudeだけを使うための場所ではない。

ClaudeもGPTもNovaも、ほかのモデルも含めて、

```text
IAM
Guardrails
Knowledge Bases
Agents
CloudWatch
CloudTrail
```

のようなAWS側の仕組みと一緒に運用する。

この違いを見て、

**あ、Bedrockの主役って「Claude」じゃなくて「AIを載せるAWS側の共通基盤」なのか。**

と腑に落ちた。

---

## Bedrockを「モデルAPI」と見るとちょっと分かりにくい

生成AIをアプリへ入れようとしたとき、自分は最初こう考えていた。

```text
Application
   ↓
API Key
   ↓
LLM Provider
```

OpenAIならOpenAI。

AnthropicならAnthropic。

Providerが増えたら、それぞれの認証情報やSDKを管理する。

普通に動く。

小さいアプリなら、むしろこれが一番分かりやすいことも多い。

でもProviderを増やしていくと、少しずつ事情が増える。

```text
OpenAI API Key
Anthropic API Key
ProviderごとのSDK
Providerごとのrequest形式
ProviderごとのRate Limit
Providerごとのログ
Providerごとの権限制御
```

モデルを増やしたかっただけなのに、アプリ側がどんどんProvider事情を知り始める。

Bedrockはここに別の境界を作れる。

```text
Application
   ↓
AWS側の認証・権限
   ↓
Amazon Bedrock
   ├─ GPT
   ├─ Claude
   ├─ Nova
   └─ ...
```

**モデルの前にBedrockを1枚置く。**

そう考えると急に分かりやすくなる。

---

## 一番「AWSだな」と思ったのはIAMだった

Bedrockを見ていて、自分が一番分かりやすく価値を感じたのはIAM。

AWS上で動かしているアプリなら、Bedrockの推論権限をIAM Roleへ持たせられる。

Converse APIを使う場合、必要になるのは基本的に `bedrock:InvokeModel`。

Streamingなら `bedrock:InvokeModelWithResponseStream` も関係してくる。

つまり、

```text
EC2 / ECS / Lambda
        ↓
      IAM Role
        ↓
    Amazon Bedrock
        ↓
許可されたModel / Inference Profile
```

という形にできる。

ここで自分の中の問題が、

> API Keyをどこに置こう？

から、

> この実行環境に何を許可しよう？

に変わった。

これ、かなりAWSっぽい。

もちろんIAMを `bedrock:*` にしてしまえば何でも呼べる。

Bedrockにした瞬間安全になるわけではない。

でも、

**生成AIの権限を既存のAWS IAM設計へ持ってこられる。**

これは、すでにAWS上でサービスを動かしているとかなり扱いやすい。

---

## そしてAPIまで「どれで呼ぶ？」になっていた

Bedrockには `InvokeModel` がある。

これは分かる。

Bedrockのモデルを呼ぶAPI。

でも今のBedrockを見ていると、APIまで選択肢が増えている。

代表的には、

```text
InvokeModel
Converse
Responses
Chat Completions
Messages
```

など。

2026年6月にはBedrock Consoleも刷新され、`bedrock-mantle` endpointを中心に、

- OpenAI Responses API
- OpenAI Chat Completions API
- Anthropic Messages API

との互換APIを扱える構成になった。

ここを見たとき、ちょっと面白かった。

**AWSのサービスなのに、OpenAIやAnthropicのAPIの顔でも呼べる。**

ProviderをBedrockへ寄せるために、アプリ側を全部「AWS独自API」へ書き換えなくてもいい方向へ進んでいる。

一方、自分が新しくBedrock向けのコードを書くなら、まず気になるのは `Converse API`。

対応モデルを共通のメッセージ形式で呼べる。

---

## TypeScriptで呼ぶと意外と普通だった

AWS SDK for JavaScript v3でConverse APIを使うと、最小構成はこんな感じになる。

```ts
import {
  BedrockRuntimeClient,
  ConverseCommand,
} from "@aws-sdk/client-bedrock-runtime";

const client = new BedrockRuntimeClient({
  region: process.env.AWS_REGION ?? "ap-northeast-1",
  maxAttempts: 5,
  retryMode: "adaptive",
});

const response = await client.send(
  new ConverseCommand({
    modelId: process.env.BEDROCK_MODEL_ID,
    messages: [
      {
        role: "user",
        content: [
          {
            text: "Amazon Bedrockを一言で説明して",
          },
        ],
      },
    ],
    inferenceConfig: {
      maxTokens: 512,
      temperature: 0.5,
    },
  }),
);

console.log(response.output?.message?.content?.[0]?.text);
```

思ったより普通。

大事なのは、

```ts
new BedrockRuntimeClient(...)
```

を作って、

```ts
new ConverseCommand(...)
```

を投げるところ。

Claude専用コードでも、GPT専用コードでもない。

モデルは `modelId` で指定する。

自分ならここもコードへ直書きせず、

```env
AWS_REGION=...
BEDROCK_MODEL_ID=...
```

のようにデプロイ設定へ逃がす。

そうすると、

**アプリのコードより、どのモデルを採用するかの方を交換しやすくなる。**

---

## ただ「modelIdを差し替えれば全部同じ」ではない

ここは少し注意。

Converse APIがあるからといって、すべてのモデルが完全に同じになるわけではない。

モデルによって、

- 対応API
- 利用可能Region
- Context Window
- Tool Use
- Reasoning系設定
- Inference Profile
- Cross-Region Inference

などは違う。

新しいモデルではInference Profile経由で使う構成もある。

なので、

> ClaudeからGPTへmodelIdだけ変えれば100%移行完了！

みたいな理解は危ない。

Bedrockが吸収してくれるのは、**差分の全部ではなく、共通化できる部分**。

ここはかなり大事だと思う。

自分なら、

```text
Application
   ↓
自分のAI Runtime境界
   ↓
Bedrock Converse
   ↓
Model
```

くらいにする。

アプリ全体がモデル固有機能へ直接依存しないようにして、どうしても必要なモデル固有機能だけ下へ逃がす。

---

## `maxTokens`、ただの生成量設定だと思ったら違った

AWSのBedrock向けガイダンスを見ていて、地味だけどかなり気になったのが `maxTokens`。

```ts
inferenceConfig: {
  maxTokens: 512,
}
```

普通に見ると、

> 長文が欲しいとき増やすやつ

くらいに感じる。

でもBedrockでは、これを明示しないことで必要以上のquotaを予約し、想定外のThrottlingにつながるケースがある。

つまり、

```text
モデル選択
    +
何tokenまで返していいか
```

まで運用設計。

例えば分類処理なら短くていい。

記事生成なら長い。

コード生成ならまた違う。

「全部8192でいいや」とすると、動くかもしれない。

でも大量に呼び始めた瞬間に、その雑さが効いてくる。

生成AIを本番へ入れると、急にこういう地味な設定が主役になってくる。

---

## GPT-6が来ても、アプリ側はGPT-6だけを見なくていい

ここで最初の話に戻る。

2026年9月22日にGPT-6 Sol / LunaがBedrockへ来た。

新しいモデルが出ると、どうしても、

> GPT-6強い！
> 使ってみたい！

という話になる。

もちろんそれは面白い。

でもBedrockを見ていると、もう一つ面白い見方ができる。

```text
昨日
Claude

今日
GPT

明日
別のModel
```

と変わっても、

その外側の、

```text
IAM
Logging
Monitoring
Guardrails
RAG
Agent Runtime
```

はできるだけ維持する。

**モデルの寿命より、アプリの寿命の方を長くしたい。**

Bedrockはそのための層として見るとかなりしっくりくる。

---

## Guardrailsを見て「これでAI安全！」とはならない

BedrockにはGuardrailsがある。

特定トピックの制御、コンテンツフィルタ、機密情報への対応などを入れられる。

強い。

でも、

```text
Guardrails通過
    ↓
本番DB DELETE
```

にはしたくない。

怖すぎる。

例えばAgentが、

> 不要な本番データを削除します

と言ったとしても、

```text
Model
 ↓
Guardrails
 ↓
Tool Call
 ↓
Application Authorization
 ↓
Human Approval
 ↓
Execute
```

くらいには分けたい。

GuardrailsはAuthorizationそのものではない。

さらにPIIを扱う場合は、レスポンス上のマスキングだけでなくCloudWatch Logs側の扱いまで確認する必要がある。

生成AIの安全機能を調べていたはずなのに、

気づいたら、

```text
IAM
KMS
Log retention
CloudTrail
```

の話をしている。

やっぱりAWSだった。

---

## そしてRAG、Agent、Memoryまで生えてくる

「LLMを呼びたい」だけなら、ここまででも十分。

でもBedrockのメニューを下へ見ていくと、まだ終わらない。

### Knowledge Bases

RAGを構築するための仕組み。

```text
User
 ↓
Query
 ↓
Knowledge Base
 ↓
関連情報
 ↓
Model
 ↓
Answer
```

### Agents

モデルにツール実行や処理フローを組み合わせる。

### AgentCore

Agentを動かすRuntime、Gateway、Memory、Identity、Observabilityなどを扱う。

2026年9月にはAgentCore Memoryで、短期Memory Eventを経由せず長期Memoryへ直接投入するAPIも追加されている。

ここまで来ると、

> Bedrock = モデルAPI

ではさすがに無理がある。

```text
Foundation Models
       ↓
Inference API
       ↓
Guardrails / Knowledge
       ↓
Agents
       ↓
AgentCore Runtime / Memory / Identity / Observability
```

**AWS、モデルを置いただけで終わる気がない。**

---

## じゃあ全部Bedrockでいいのか？

ここまで書くと、

> じゃあOpenAIやAnthropicを直接使わず、全部Bedrockでよくない？

となる。

自分はそうは思わない。

Provider APIを直接使う方が自然なケースもある。

例えば、

- Providerの最新機能を最速で使いたい
- Provider固有APIをかなり使いたい
- AWSへ寄せる理由が薄い
- 小さなPoCなので構成を最小にしたい

なら、直接APIは普通に候補。

Claudeについては、AWS自身がClaude Platform on AWSという別ルートも用意している。

一方、

- すでにAWS上でサービスを動かしている
- IAMへ認証・認可を寄せたい
- 複数Providerを使いたい
- モデル交換を前提にしたい
- Guardrails / Knowledge Bases / Agentsを使いたい
- CloudWatch / CloudTrailまで含めて運用したい

なら、Bedrockがかなり面白くなる。

自分の中ではこう。

```text
「このモデルを使いたい」
        ↓
Provider Native APIも強い

「AIをAWSシステムとして運用したい」
        ↓
Bedrockが強くなる
```

---

## 今回はGPT-6を実際には回していない

ここは明確にしておく。

今回は、

- Amazon Bedrock公式ドキュメント
- 2026年9月のAWS公式発表
- Converse API / AWS SDK仕様
- IAM / Guardrails / AgentCore関連仕様

を確認して記事を書いている。

接続中のAWS環境でもBedrockのモデル一覧を取得しようとしたが、今回使っているAWS連携では対象operationが公開されておらず、アカウント固有の利用可能モデル一覧までは確認できなかった。

そして意図しない課金を避けるため、GPT-6やClaudeへの有料推論も実行していない。

なので、

- GPT-6 Solは実際どれくらい速いか
- Claude Sonnet 5.5との品質差
- 自分の環境でのtoken単価
- 実際のThrottling発生条件

は、この記事では評価していない。

**ニュースを見て「すごそう」で終わらず、今のBedrockがどういう立ち位置になっているのかを公式仕様から追った。**

今回はそこまで。

---

## まとめ

最初：

> Amazon Bedrock？
> AWSからClaude呼ぶやつでしょ。

2026年9月22日：

> GPT-6 Sol / Lunaも来た。

9月28日：

> Claude Sonnet 5.5も来た。

モデル一覧を見る：

> GPT、Claude、Nova、DeepSeek、Kimi、xAI……

自分：

> **AWS、AIモデルのセレクトショップみたいになってない？**

でも調べていくと、面白かったのはモデル数そのものではなかった。

Bedrockを1枚挟むことで、

```text
Model
  ↑
Bedrock
  ↑
IAM / API / Guardrails / Knowledge / Agent
  ↑
Application
```

という境界を作れる。

新しいモデルが出るたびにアプリ全体を作り直すのではなく、

**モデルは交換する。でも、その外側の運用基盤は残す。**

Bedrockはそのための場所として見るとかなり分かりやすかった。

GPT-6がBedrockへ来たニュースを見て、

「AWSでもGPT-6が使えるんだ」

で終わるつもりだった。

気づいたら、

**「これ、モデルを選ぶサービスというより、AIモデルが次々変わることを前提にしたAWSの層なんじゃないか？」**

というところまで来ていた。

たぶん次に新しいモデルがBedrockへ追加されても、見る場所はモデルの性能だけじゃない。

> このモデル、既存のIAM・API・Guardrails・Agent基盤へどこまでそのまま載るんだろう？

そっちが気になる。

---

## 参考

- [OpenAI GPT-6 Sol and GPT-6 Luna are now generally available on Amazon Bedrock](https://aws.amazon.com/about-aws/whats-new/2026/09/openai-gpt-6-sol-luna-on-amazon-bedrock/)
- [Claude Sonnet 5.5 now available on AWS](https://aws.amazon.com/about-aws/whats-new/2026/09/claude-sonnet-5-5-aws/)
- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- [Models at a glance - Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html)
- [API compatibility - Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-api-compatibility.html)
- [Inference using Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Amazon Bedrock redesigned console / OpenAI- and Anthropic-compatible APIs](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-redesigned-console-optimized-openai-anthropic-compatible-apis/)
- [Amazon Bedrock AgentCore Memory direct ingestion](https://aws.amazon.com/about-aws/whats-new/2026/09/agentcore-memory-direct-ingest/)
