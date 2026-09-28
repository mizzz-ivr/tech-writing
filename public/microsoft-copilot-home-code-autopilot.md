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

基盤にはGitHub Copilotと同じ技術が使われていますが、Microsoftはソフトウェア開発者の日常的な開発では引き続きGitHub Copilotを使うと説明しています。

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

- Microsoft Japan: Home、Code、Autopilot を備えた新しい Copilot を発表  
  https://news.microsoft.com/source/asia/features/introducing-the-new-copilot-with-home-code-and-autopilot/?lang=ja

- Microsoft: Copilot Managed Runtime  
  https://www.microsoft.com/en-us/copilot/blog/copilot-studio/build-where-you-want-run-with-confidence-now-microsoft-hosts-and-manages-the-code-created-by-copilot/
