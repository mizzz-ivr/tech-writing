---
title: Microsoft Copilotに「Code」と「Autopilot」が生えた。これ、AIチャットじゃなくて仕事のOSでは？
tags:
  - MicrosoftCopilot
  - Microsoft365
  - AI
  - 生成AI
  - AIエージェント
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

2026年9月25日、MicrosoftがCopilotの大規模アップデートを発表しました。

追加された中心機能は **Home / Code / Autopilot**。

最初は、

> Copilotにまた機能が増えたのか。

くらいに思っていました。

でも3つを並べてみると、少し見え方が変わります。

```text
質問する
  ↓
Chat

仕事をまとめて任せる
  ↓
Cowork

必要なアプリや自動化を作る
  ↓
Code

人間が離れても仕事を続ける
  ↓
Autopilot
```

**Microsoftが作ろうとしているのは、単なるAIチャットではなく「仕事を始める場所そのもの」なのかもしれません。**

今回は、発表内容を追いながら「何が変わったのか」を短く整理します。

> この記事は2026年9月28日時点のMicrosoft公式情報をもとにしています。

---

## これまでのCopilotと、何が違う？

ここが今回いちばん分かりにくいところです。

これまでのCopilotでも、かなりいろいろできました。

たとえば、

- 先週のメールを要約する
- 未返信メールを探す
- メールの返信案を作る
- 会議を設定する
- Wordの文章を下書きする
- PowerPointの内容を整理する
- Excelのデータについて質問する

といったことです。

2025年のMicrosoft 365 Copilotを見ても、メール・会議・文書を横断して情報を探したり、下書きを作ったりするところまではかなり進んでいました。

ただ、基本的な流れはまだ、

```text
人間が依頼する
   ↓
Copilotが答える・作る
   ↓
人間が確認する
   ↓
次の作業をまた依頼する
```

という形が中心でした。

もちろんCopilot StudioやAgentsなど、自動化の仕組み自体は以前からあります。

それでも、**普段使うCopilotそのものに「アプリを作る」「仕事を丸ごと委任する」「数日後も自律的に続きを進める」能力が、ここまで一体化されてはいませんでした。**

今回のアップデートで変わるのは、この「扱う仕事の大きさ」です。

| これまでのCopilot | 今回のCopilotで期待されること |
| --- | --- |
| メールを要約する | 関連情報を集めて仕事全体を進める |
| 会議の候補を出す・設定する | プロジェクトの予定を組み、後続作業まで追う |
| 文書やスライドを作る | 成果物一式をまとめて作る |
| コードや式の案を出す | 業務用アプリやダッシュボードそのものを作る |
| プロンプトを送ると動く | PCを閉じても継続して仕事を進める |

単に「回答が賢くなった」というより、

**人間が途中の工程をつないでいた仕事を、より大きな単位でCopilotへ渡せるようにしようとしている。**

というのが今回の変化だと思います。

---

## Home：まず「Copilotを開く」が入口になる

Homeは、新しいCopilotのスタート地点です。

ChatとCoworkがまとまり、さらにWord・Excel・PowerPointの機能もCopilot内から使えるようになります。

ざっくり言えば、

```text
今まで
Wordを開く
Excelを開く
PowerPointを開く
Teamsを開く

これから
Copilotを開く
  ↓
必要な仕事を進める
```

という方向です。

もちろんOfficeアプリがなくなるわけではありません。

ただ、**「どのアプリを開くか」より先に「何をしたいか」をCopilotへ伝える**流れが強くなっています。

---

## Code：GitHub Copilotとは別の「作る場所」

個人的に一番気になったのがCodeです。

名前だけ見ると、

> GitHub Copilotがあるのに、またCode？

となります。

ただ、対象が少し違います。

Microsoftの説明では、Codeは自然言語からアプリや自動化を作るための機能です。

たとえば、

- 社内用の簡単なアプリ
- ダッシュボード
- 定型作業の自動化
- 業務フロー用の小さなツール

といったものを、Copilot上で作っていくイメージです。

Microsoftによると、CodeはGitHub Copilotと同じ基盤技術（underlying technology）を利用しています。ただし、ソフトウェア開発者の日常的な開発では引き続きGitHub Copilotを使うと説明しています。

つまり、

```text
GitHub Copilot
→ ソフトウェア開発者の開発を支援

Copilot Code
→ より多くの人が業務用の仕組みを作る
```

という棲み分けになりそうです。

そして、作ったコードをMicrosoft 365環境内で動かすための **Copilot Managed Runtime** も発表されています。

「コードを書いて終わり」ではなく、

**作る → 動かす → 組織内で管理する**

までをCopilot側へ寄せようとしているのが面白いところです。

---

## Autopilot：「聞いたら答える」から離れていく

Autopilotは、以前Scoutと呼ばれていた機能です。

名前・役割・目標を設定すると、ユーザーから毎回プロンプトを送らなくても仕事を続けます。

Microsoftが挙げている例では、

- チャネルを確認する
- スレッドを追う
- フォローアップする
- 定期作業を実行する
- 数日後にプロジェクトの続きを再開する

といった動きが紹介されています。

しかもクラウド上で動くため、PCを閉じていても処理を続けられます。

ここまで来ると、

```text
従来のCopilot
人間「これやって」
AI「できました」

Autopilot
人間「この役割と目標で動いて」
AI「継続して進めます」
```

という違いが大きいです。

「AIアシスタント」というより、Microsoftが表現する **デジタルのチームメイト** に近づいています。

---

## 例えば「新製品のローンチ準備」を任せるとしたら

今回のアップデートが分かりやすいのは、1つの仕事に当てはめたときです。

例えば、

> 来月の新製品ローンチに必要な準備を進めて。

とCopilotへ頼む場面を考えてみます。

これまでなら、

```text
メール・Teamsから情報を探す
↓
Copilotに要約してもらう
↓
人間が計画を整理する
↓
資料を作らせる
↓
進捗表を作る
↓
関係者へ確認する
↓
数日後、また状況を確認する
```

というように、**Copilotを使いながらも工程同士をつなぐのは人間**でした。

今回の新しい構成なら、将来的にはこんな使い方が見えてきます。

```text
Home / Cowork
→ メール・会議・資料をもとにローンチ計画と資料を作る

Code
→ 進捗を確認する専用TrackerやDashboardを作る

Autopilot
→ Teamsのやり取りを追う
→ 未回答の担当者へフォローする
→ 定期的に進捗を確認する
→ 数日後も続きを進める
```

つまり、欲しいのが「メールの要約」ではなく、

**「ローンチ準備を前に進めておいて」**

というレベルの依頼になってきます。

MicrosoftがAutopilotの例として挙げているサプライヤーレビューでも、スケジュール作成だけではなく、準備・会議・フォローアップ・関係者への確認まで継続的に扱う想定になっています。

もちろん、Home / Code / Autopilotはまだ展開途中なので、今すぐこの一連の流れをそのまま使えるという意味ではありません。

ただ、**今回Microsoftが目指しているCopilotの使われ方**は、このくらいの粒度だと考えるとかなり分かりやすいです。

---

## じゃあ、ChatGPTやClaudeと何が違う？

ここまで読むと、

> でもChatGPTやClaudeも、もう似たことできるのでは？

と思います。

これはその通りです。

2026年9月時点では、**「複数ステップの仕事を丸ごと任せる」こと自体はCopilotだけの特徴ではありません。**

ChatGPTには **Work** があり、接続したアプリやクラウドブラウザを使って複数ステップのWeb作業を進められます。タスクによっては、PCを閉じたあともクラウド側で処理を続けられます。

Claudeにも **Cowork** があり、ローカルファイル・ブラウザ・接続サービスをまたいで、成果物が完成するまでの仕事をまとめて委任できます。開発寄りの仕事にはClaude Codeもあります。

ざっくり並べると、こんな違いに見えます。

| | 得意としている方向 |
| --- | --- |
| ChatGPT Work | Web・外部サービス・各種アプリを横断して仕事を実行する |
| Claude Cowork / Code | ローカルファイルやツールを使った長い作業、知識労働・開発を進める |
| 新しいMicrosoft Copilot | Microsoft 365の中で、仕事・アプリ作成・継続エージェントを一体化する |

なので、今回のCopilotを

**「ChatGPTやClaudeではできなかったことが突然できるようになった」**

と見るのは少し違います。

むしろ面白いのは、Microsoftがこれを **Teams / Outlook / Word / Excel / PowerPointと同じ仕事環境の中に入れようとしていること** です。

AutopilotはMicrosoft 365のテナント内に独自のID・メモリ・コンピューター・ワークスペースを持ち、TeamsやOutlookなど既存の仕事場に現れる設計になっています。

つまり競争軸は、

```text
AIがどれだけ賢いか
        ↓
AIにどこまで仕事を任せられるか
        ↓
会社の仕事環境そのものを
どのAIが握るか
```

へ移ってきているように見えます。

ChatGPTは幅広いサービスを横断する方向、ClaudeはCoworkやCodeで実作業を深く任せる方向、MicrosoftはMicrosoft 365そのものをAI中心の仕事環境へ組み替える方向。

今回のアップデートで、Copilotもこの競争にかなり本格的に入ってきた印象です。

---

## 3つを並べると狙いが見える

今回の発表を機能ごとに見ると、こんな感じです。

| 機能 | 役割 |
| --- | --- |
| Home | 仕事を始める |
| Chat | 質問・相談する |
| Cowork | まとまった仕事を任せる |
| Code | 必要なアプリや自動化を作る |
| Autopilot | 継続的に仕事を進める |

これを見ていて思ったのが、

**MicrosoftはCopilotを「Officeに付いているAI」から、「仕事全体の入口」へ移そうとしているのでは？**

ということでした。

WordやExcelをAI化するだけではなく、

```text
考える
↓
作業する
↓
ツールを作る
↓
継続運用する
```

までをCopilotの中でつなごうとしています。

Microsoft自身も今回の発表で、Copilotを「new OS for work」と表現しています。

「OS」と言われると少し大げさにも見えますが、Home / Code / Autopilotを並べると、狙っている方向は分かりやすいです。

---

## ただし、全部が今すぐ使えるわけではない

ここは注意が必要です。

2026年9月28日時点では、

- Home / Code：Frontierプログラムへ順次展開
- Autopilot：9月末にPrivate Previewを拡大
- Code：Microsoft 365 Premium / Pro向けPreviewは今年後半予定
- Copilot Managed Runtime：Preview

という段階です。

なので、この記事は「全部使ってみたレビュー」ではありません。

現時点では、**MicrosoftがCopilotをどこへ持っていこうとしているのかを、公式発表から整理したもの**です。

---

## まとめ

今回の発表を最初に見たときは、

> Home、Code、Autopilotが追加された。

という機能アップデートに見えました。

でも少し追ってみると、

```text
Home
  ↓
仕事の入口

Code
  ↓
仕事に必要な仕組みを作る

Autopilot
  ↓
仕事を継続して動かす
```

と、それぞれ役割がつながっています。

これまでのCopilotは「使っているアプリの横にいるAI」という印象が強かったです。

今回のアップデートを見る限り、Microsoftはその位置を少し変えて、

**「まずCopilotを開いて、そこから仕事を始める」**

世界を作ろうとしているように見えます。

本当に「仕事のOS」まで育つのか。

今後のCodeとAutopilotの展開は、かなり気になります。

---

## 参考

- Microsoft: Introducing the new Copilot with Home, Code and Autopilot  
  https://blogs.microsoft.com/blog/2026/09/25/introducing-the-new-copilot-with-home-code-and-autopilot/

- Microsoft: Copilot Managed Runtime  
  https://www.microsoft.com/en-us/copilot/blog/copilot-studio/build-where-you-want-run-with-confidence-now-microsoft-hosts-and-manages-the-code-created-by-copilot/

- Microsoft Support: How Copilot Chat works in Microsoft 365 apps  
  https://support.microsoft.com/en-us/microsoft-365-copilot/how-copilot-chat-works-in-microsoft-365-apps

- OpenAI: Using cloud browser in ChatGPT  
  https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt

- Anthropic: Cowork Workshop: Foundations  
  https://www.anthropic.com/webinars/cowork-workshop-foundations
