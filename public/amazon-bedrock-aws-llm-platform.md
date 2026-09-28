---
title: Amazon Bedrock、ただの「AWS版LLM API」だと思ってた
tags:
  - AWS
  - AmazonBedrock
  - 生成AI
  - TypeScript
  - 個人開発
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

Amazon Bedrock、最初はかなり勘違いしていた。

自分の中では、

> AWSからClaudeとかNovaを呼べるAPIでしょ？

くらいの認識だった。

要するにこう。

```text
自分のアプリ
   ↓
Amazon Bedrock
   ↓
Claude / Nova / Llama ...
```

もちろん、これは間違いではない。

でも公式ドキュメントを追っていくと、だんだん見え方が変わってきた。

**Bedrockの面白さは「モデルを呼べること」より、その前後をAWSの仕組みで組めることにある。**

IAMで「誰がどのモデルを呼べるか」を絞る。

Converse APIでモデルごとの差を少し薄くする。

Guardrailsで入力・出力にガードを置く。

Knowledge BasesでRAGを組む。

必要ならAgentsやAgentCoreまで広げる。

気づいたら、

```text
LLM API
```

を探していたはずなのに、

```text
生成AIをAWS上で運用するための基盤
```

を見ていた。

今回はAmazon Bedrockを「モデル一覧」からではなく、**実際にアプリへ入れるなら何が変わるのか**という視点で整理してみる。

---

## 最初は「APIキーをどこに置く？」から考えていた

生成AIをアプリに入れようとすると、まず気になるのが認証情報。

例えばProviderのAPIを直接使うなら、だいたいこうなる。

```text
Application
   ↓
API Key
   ↓
LLM Provider
```

当然、そのAPI Keyをコードへ直書きするわけにはいかない。

環境変数に入れる。

Secrets Managerへ置く。

ローテーションを考える。

漏れたときの失効手順も考える。

Providerが増えれば、管理するSecretも増える。

自分は最初、Bedrockもこの延長だと思っていた。

「AWSからモデルを呼べるなら、Bedrock用のAPI Keyを持つのかな」

でも、ここで考え方が変わる。

Bedrockの推論APIはAWSのIAM権限で制御できる。

Converse APIを使う場合も、必要になるのは `bedrock:InvokeModel`。

つまりAWS上のアプリなら、

```text
Application
   ↓
IAM Role
   ↓
Amazon Bedrock
   ↓
Foundation Model
```

という構成にできる。

**「APIキーを安全に保存する」から、「この実行環境に何を許可するか」へ問題が変わる。**

ここが最初に「思ってたのと違う」と感じたところだった。

---

## 「Claudeを呼ぶコード」ではなく「Bedrockを呼ぶコード」にできる

次に気になったのがAPI。

モデルが増えるたびにrequest形式まで変わると、結局Providerごとの分岐が増える。

```ts
if (provider === "anthropic") {
  // Anthropic形式
}

if (provider === "amazon") {
  // Nova形式
}

if (provider === "meta") {
  // Llama形式
}
```

これをやり始めると、モデルを切り替えたいだけなのにアプリ側のコードがProvider事情をどんどん知ることになる。

Bedrockには `InvokeModel` もあるけど、AWSはメッセージ形式を扱う用途として `Converse` / `ConverseStream` を用意している。

Converse APIは、対応モデルに対して共通の会話形式で呼び出せる。

イメージとしてはこう。

```text
Application
   ↓
Converse API
   ├─ Claude
   ├─ Nova
   └─ Llama
```

モデル固有機能が完全になくなるわけではない。

でも、「まず会話させる」という基本部分はかなり揃えられる。

TypeScriptなら最小構成はこんな感じ。

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
        content: [{ text: "Amazon Bedrockを一言で説明して" }],
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

Provider SDKを直接呼ぶコードではなく、Bedrock Runtimeを呼ぶ。

モデルを変えるときは、まず `modelId` を変える。

この境界はかなり分かりやすい。

---

## ただし、`modelId`を文字列で置けば終わりではなかった

ここで「じゃあモデル名だけ差し替えれば全部終わり？」と思った。

そんなに単純ではなかった。

Bedrockでは、利用するモデルやリージョンによって、

- Foundation Model ID
- Inference Profile
- Cross-Region Inference

あたりを意識する必要がある。

新しいモデルでは、直接のModel IDではなくInference Profile経由で呼ぶケースもある。

Cross-Region Inferenceを使う場合は、地理的な範囲も設計要素になる。

つまり、

```text
ClaudeだからこのID
```

と記事へ固定値を書いて終わりにすると、すぐ古くなりそう。

なので自分なら、アプリ側はこうする。

```env
BEDROCK_MODEL_ID=<deploymentごとに設定>
AWS_REGION=<利用リージョン>
```

コードへモデルIDを埋め込まない。

そしてデプロイ時や運用時に、AWSの最新のモデル一覧・Inference Profileを確認する。

「モデルを抽象化できる」と「モデル事情を知らなくていい」は別。

ここは分けて考えた方がよさそうだった。

---

## `maxTokens`を省略しない方がいい、という地味だけど重要な話

Bedrockの資料を見ていて、かなり地味だけど気になったのが `maxTokens`。

Converse APIの例では、最大出力トークン数を明示できる。

```ts
inferenceConfig: {
  maxTokens: 512,
}
```

これを「必要になったら設定すればいいオプション」くらいに見ない方がよさそう。

AWSのBedrock向けガイダンスでは、出力上限を明示しないことで必要以上のquotaを予約し、想定外のThrottlingにつながるケースが注意されている。

なので、

> とりあえずモデル最大値で

ではなく、

> この処理は何token返れば十分か

をアプリ側で決める。

例えば分類なら512もいらないかもしれない。

長文生成なら数千必要かもしれない。

同じモデルでも用途で変わる。

生成AIのコスト・quota設計って、モデル選択だけじゃない。

**1回の呼び出しにどこまで出力を許すかも、ちゃんと運用設定だった。**

---

## IAMにすると「誰でもBedrockを呼べる」を避けやすい

BedrockをAWS上で使う意味として、個人的に一番分かりやすかったのはIAM。

最初は開発を早く進めるために、広めの権限を付けたくなる。

でも本番で、

```json
{
  "Effect": "Allow",
  "Action": "bedrock:*",
  "Resource": "*"
}
```

みたいな状態にはしたくない。

例えば推論だけなら、必要なActionはかなり絞れる。

Converseなら基本は `bedrock:InvokeModel`。

Streamingするなら `bedrock:InvokeModelWithResponseStream` も必要になる。

そしてResourceも、利用するFoundation ModelやInference Profileへ絞れる。

構成としては、

```text
API Server Role
  ↓
許可されたBedrock推論だけ
  ↓
利用を認めたModel / Inference Profile
```

にできる。

ここで大事なのは、Bedrockを使うだけで勝手に安全になるわけではないこと。

結局、IAMを広くすれば広く使える。

だからBedrockを選ぶ理由は、

**「安全」ではなく「AWSの権限制御へ乗せられる」**

くらいに考えるのがちょうどよさそう。

---

## Guardrailsを見て「これで全部安全」……ではなかった

BedrockにはGuardrailsもある。

不適切な内容、特定トピック、機密情報などに対して制御を入れられる。

ここだけ見ると、

> じゃあGuardrailsを入れればAIの安全対策は終わり？

と思いそうになる。

当然そんなことはない。

Guardrailsは強い機能だけど、アプリ側のAuthorizationまで代わりにやってくれるわけではない。

例えばAIがTool Useで、

> 本番DBの古いレコードを削除します

と言ったとして。

Guardrailsを通過したから、そのままDELETEを許可する。

これは怖い。

```text
LLM
 ↓
Guardrails
 ↓
Tool Call
 ↓
Application Authorization
 ↓
必要ならHuman Approval
 ↓
実行
```

Guardrailsはガードの1層。

DB削除権限や決済権限までAIへ委ねる話とは別。

さらに、PIIのマスキングを使う場合もログ設計まで見る必要がある。

AWSのBedrock向けガイダンスでは、レスポンス上でマスクしていても、CloudWatch Logs側に元データが残る構成には注意が必要とされている。

KMS暗号化、IAM、ログ保持期間。

AIの安全機能を見るつもりが、普通にインフラ運用の話へ戻ってくる。

**ここもAWSっぽい。**

---

## その先を見ると、もう「LLM API」ではなかった

ここまででも、

- IAM
- Converse API
- Inference Profile
- Guardrails

が出てきた。

でもBedrockはこの先もある。

### Knowledge Bases

RAGを組むための仕組み。

```text
User
 ↓
Query
 ↓
Knowledge Base
 ↓
関連情報を取得
 ↓
Model
 ↓
Response
```

「PDFをS3へ置いて、Vector DBを自前で全部組んで……」だけが選択肢ではなくなる。

### Agents

モデルにAction Groupなどを組み合わせて、外部処理を実行するAgentを作れる。

### AgentCore

AgentをRuntimeとしてデプロイしたり、Gateway、Memory、Identity、Observabilityなどを組み合わせる領域まで広がる。

ここまで来ると、自分の最初の認識だった、

> AWSからClaudeを呼べるAPI

では説明が足りない。

Bedrockは、

```text
Model Invocation
     +
IAM / Guardrails
     +
RAG / Agents
     +
Runtime / Observability
```

まで同じAWS側で考えられる。

だから「どのLLMが使える？」だけ見ていると、Bedrockの半分くらいしか見ていない気がする。

---

## じゃあProvider APIを直接使わず、全部Bedrockでいい？

ここで逆に思った。

> じゃあ生成AIは全部Bedrockでよくない？

これも違うと思う。

Provider APIを直接使う方が自然なケースもある。

例えば、

- Provider最新機能を最速で使いたい
- AWSへ寄せる理由が薄い
- 小さな検証でIAM設計まで持ち込みたくない
- Provider固有APIを強く使いたい

なら、直接APIの方がシンプルかもしれない。

一方で、

- すでにAWS上でアプリを動かしている
- IAM Roleで権限をまとめたい
- 複数モデルを同じRuntime APIから扱いたい
- RAG / Guardrails / Agent系までAWSで組みたい
- CloudTrailやCloudWatchを含めて運用したい

なら、Bedrockの価値がかなり出てくる。

自分の中では、こう整理した。

```text
「モデルを使いたい」
     ↓
Provider APIでもBedrockでもできる

「生成AIをAWS上のシステムとして運用したい」
     ↓
Bedrockがかなり気になってくる
```

---

## 今回は有料の推論までは実行していない

ここは明確にしておく。

今回はAWS公式ドキュメント、Bedrock向けのAPI・IAM・SDK仕様を確認して記事にしている。

接続中のAWS環境でもモデル一覧の読み取りを試したが、今回使っているAWS連携では対象のBedrock operationが公開されておらず、アカウント固有の利用可能モデルまでは確認できなかった。

また、意図しない課金を避けるため、モデルの推論呼び出しは実行していない。

なのでこの記事では、

- 実際のレスポンス速度
- モデル品質
- 自分のAWSアカウントでの実測コスト
- Throttlingの再現結果

までは評価していない。

ここを「試した結果」とは書かない。

今回やったのは、**Bedrockをアプリへ組み込むと何が変わるのかを、公式仕様から設計レベルまで追ったこと**。

そして、一番大きく変わったのは認識だった。

---

## まとめ

最初の自分：

> Amazon Bedrock？ AWS版のLLM APIでしょ？

調べたあと：

> あ、モデルを呼ぶところより、その前後をAWSで組めるのが本体かも。

となった。

Converse APIでモデル呼び出しの形を揃える。

IAMで実行権限を絞る。

Inference Profileやリージョンを運用設定として扱う。

`maxTokens`までquota設計として考える。

Guardrailsを入れても、Authorizationは別に残す。

必要になればKnowledge Bases、Agents、AgentCoreへ広げる。

```text
Application
   ↓
IAM
   ↓
Bedrock Runtime
   ↓
Converse
   ↓
Foundation Model
   ↓
Guardrails / RAG / Agent
   ↓
CloudWatch / CloudTrail
```

こうして見ると、Bedrockは「ClaudeやNovaを呼べるサービス」というより、

**生成AIを既存のAWSシステムへどう入れるかを考える場所**

に近い。

モデルを1回呼ぶだけなら、もっと簡単な方法もある。

でも「本番で誰に何を許す？」「モデルを変えたら？」「RAGは？」「ログは？」「AIにどこまで権限を渡す？」まで考え始めた瞬間、Bedrockの見え方が一気に変わった。

次にBedrockを見るときは、モデル一覧より先にIAMとConverse APIを見そう。

---

## 参考

- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [Inference using Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [APIs supported by Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/apis.html)
- [Supported foundation models in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
- [Cross-region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)
- [Security in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/security.html)
- [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
