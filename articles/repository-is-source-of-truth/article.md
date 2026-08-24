---
title: "AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話"
status: draft
topics:
  - ai-development
  - individual-development
  - github
source_repositories:
  - https://github.com/ivRooom/Herta
published:
  qiita: null
  zenn: null
---

# AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話

個人開発でAIを使っていると、たまに変なことが起きます。

「次に何を実装しよう？」と聞いたら、AIがそれっぽい機能をいくつか提案してくれる。

「いいじゃん、それ作ろう」と思ってRepositoryを見てみたら、もうある。

しかも自分で作ってる。

最近開発しているDiscord向けのプロジェクトでも、追加候補として考えていた機能がすでにPluginとして実装されていました。単にコマンドだけあるわけではなく、再試行や復旧まで考えた実装になっていて、自分のRepositoryなのに普通に忘れていました。

最初は「AIが過去の会話をもっと覚えていれば解決するのでは？」と思っていたんですが、開発を続けていくうちに、どうもそこじゃないなと思うようになりました。

会話も古くなるし、READMEも古くなる。Issueだって更新を忘れます。

だったらAIに昔の会話を頑張って覚えてもらうより、今のRepositoryを見てもらえばいい。

そこから、自分のAI開発エージェントには

> Repository is the Source of Truth

というルールをかなり強く入れるようになりました。

この記事では、実際に個人開発でこの運用を続けてみて、何が変わったのかを書いていきます。

## 以前は「現在地点」をプロンプトに書いていた

<!-- 過去の使い方、長い引き継ぎプロンプト、状態が古くなる問題 -->

## IssueもREADMEも普通に古くなる

<!-- stale Issue / 実装済みなのに未完了に見えるケース -->

## Repository is the Source of Truth にした

<!-- 何を確認させるか。Repositoryだけを見る、という意味ではないことも説明する -->

## 既存機能を再実装しなくなった

<!-- Poll / Reminderなど、実際にRepository確認で重複候補を避けられた例。公開前に最新コードを再検証する -->

## 「次に何を作るか」も任せやすくなった

<!-- Issue / PR / TODO / Docs / Tests / Security / UXなどから次タスクを選ぶ流れ -->

## コードを書かせるより、開発ループを回してもらう

<!-- 調査 → タスク選定 → 実装 → Test → CI → Review → PR -->

## Repositoryだけで全部解決するわけではない

<!-- GitHub Issue / PR / Docs / Notion / 会話の役割分担 -->

## 個人開発だからこそ効いた部分

<!-- コンテキスト復元コスト、数日空いた後の再開など -->

## まだ人間側に残していること

<!-- Product direction / production changes / merge decision / risky operations -->

## まとめ

<!-- きれいに一般化しすぎず、今の自分なりの結論で締める -->
