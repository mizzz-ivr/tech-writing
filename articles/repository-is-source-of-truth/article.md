---
title: AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話
status: published
published_at: '2026-08-24'
article_type: case-study
level: intermediate
topics:
- ai-development
- individual-development
- github
domains:
- ai
- developer-productivity
languages: []
technologies:
- GitHub
- GitHub Issues
- GitHub Pull Requests
- GitHub Actions
portfolio_signals:
- development-process
- ai-assisted-development
source_repositories:
- ivRooom/Herta
published:
  qiita: https://qiita.com/mizzz-ivr/items/44cd3077d732eea1bf6e
  zenn: null
---

# AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話

個人開発でAIを使っていると、たまに変なことが起きます。

「次に何を実装しよう？」と聞くと、それっぽい機能をいくつか提案してくれる。便利そうだし、そのまま作ろうかなと思ってRepositoryを見たら、もうある。

しかも自分で作ってる。

最近開発しているDiscord向けのプロジェクトでも、PollやReminderを次の候補として考えたことがありました。ところがコードを確認すると、どちらもすでにPluginとして存在していました。

Reminderは `/remind set`、`list`、`cancel` があるだけではなく、配信失敗時のretryや、処理途中で止まったReminderの復旧まで入っていました。Pollも作成・一覧・結果確認・終了に加えて、Buttonで投票できるところまで実装済みでした。

自分のRepositoryなのに、普通に忘れていました。

最初は「AIが過去の会話をもっと覚えていれば解決するのでは？」と思っていたんですが、開発を続けていくうちに、どうもそこじゃないなと思うようになりました。

会話も古くなるし、READMEも古くなる。Issueだって更新を忘れます。

だったら、AIに昔の会話を頑張って覚えてもらうより、今のRepositoryを見てもらえばいい。

そこから、自分のAI開発エージェントには

> Repository is the Source of Truth

というルールをかなり強く入れるようになりました。

これを始めてから、AIに「コードを書いてもらう」というより、Repositoryの現在地点を一緒に確認しながら開発を進める感覚に変わってきました。

## 以前は「現在地点」をプロンプトに書いていた

AIを開発に使い始めた頃は、引き継ぎ用のプロンプトをかなり細かく書いていました。

```text
現在ここまで実装済みです。
次はこの機能を実装してください。
その後はこのIssueを進めてください。
```

短い開発ならこれでも困りません。

でも、個人開発を何週間、何か月と続けていると、この「現在ここまで」が思った以上に早く古くなります。

ある機能を実装してPRをマージする。別の機能を直す。途中で設計を変える。Issueも増える。数日後に別のチャットから続きを始める。

そのたびに、前回のプロンプトに書かれていた現在地点とmain branchの状態が少しずつズレていきます。

最初は引き継ぎ文を更新していました。でも、だんだん「この情報を維持するための作業」が増えてきました。

それなら、現在地点そのものをプロンプトに固定するのではなく、**現在地点の調べ方をプロンプトに固定した方が楽なのでは**、と考えるようになりました。

## IssueもREADMEも普通に古くなる

「じゃあIssueを見ればいいのでは？」とも思いました。

これも実際にやってみると、完全ではありませんでした。

HertaにはStudioのCommand PaletteをHybrid / Vector Search対応するIssueがあります。Issue本文だけを見ると、semantic searchはまだ未対応で、これから実装するように読めます。

ところが現在のRepositoryを見ると、`POST /api/search/semantic` はすでに存在しています。

現行のDocsにも、

```text
label exact
keyword exact
label prefix
keyword prefix
lexical phrase / token match
static intent match
semantic similarity
```

という検索順序が書かれていて、semantic scoreは既存のlexical結果を追い越さない設計になっています。

さらに、providerが失敗した場合はlexical searchへfallbackすること、request rateやbody sizeを制限すること、実Guild IDやGuild名をembedding用のcorpusへ含めないことまで実装・文書化されています。

でもIssueはopenのままです。

Issueが間違っているというより、**Issueは「何をやりたいか」を残す場所で、常に現在の実装状態を表すとは限らない**というだけなんですよね。

READMEも同じです。Repositoryが大きくなれば、コードを変更するたびに全ドキュメントを完全同期するのは難しくなります。

この経験から、AIには

```text
Issueがopenだから未実装、と判断しない。
READMEに書かれていないから存在しない、と判断しない。
対象コード、PR、Docs、Testsまで確認する。
```

というルールを入れるようになりました。

## 「Repository is the Source of Truth」にした

ここで言うRepository is the Source of Truthは、「コード以外は信用しない」という意味ではありません。

Issueも読むし、PRも読むし、Docsも読みます。設計の背景を知るには、むしろコードだけでは足りません。

ただ、情報が食い違ったときに、**「今、実際に何が存在しているのか」は現在のRepositoryで確認する**ようにしました。

自分の開発エージェントには、作業前にだいたい次の順番で確認させています。

```text
main / default branch
        ↓
最近のPR・Issue
        ↓
対象コード
        ↓
Tests / Migration / Docs
        ↓
CI
        ↓
現在地点を整理
```

ポイントは、プロンプト側に「Pollは未実装」「Birthday Cardは次に作る」のような現在状態を大量に書かないことです。

現在状態は変わります。

一方で、

> 作業開始前にRepositoryを確認する

というルールは、機能が増えてもあまり変わりません。

長い引き継ぎプロンプトを毎回最新化するより、この方が自分の開発では扱いやすくなりました。

## 自分で作った機能を、もう一度作りそうになった

この考え方が一番分かりやすく効いたのが、新機能を考えているときでした。

Discord Botのコマンドをもっと増やそうとしていたとき、PollとReminderはかなり自然な候補でした。

ただ、実際にRepositoryを調べてみると、すでにありました。

Reminderは一定時間後にメッセージを送るだけではなく、DM / channelの配信先選択、ユーザーごとの上限、30秒周期の処理、配信失敗時の再試行、stale状態の復旧まで持っています。

Pollも単純なリアクション投票ではなく、2〜10件の選択肢、単一・複数選択、結果表示、Button interaction、期限切れPollの終了処理まであります。

ここまで作っているのに、次の実装候補として普通に考えていました。

たぶん個人開発を長くやっている人なら、似たような経験があると思います。

「自分が書いたコードなんだから全部覚えている」は、規模が小さいうちだけでした。

AIがRepositoryを調べるようにしてからは、

> Pollを作る

ではなく、

> 現在のPollに足りないものは何か

から考えられるようになりました。

これはコード生成の精度が上がったというより、**そもそも間違ったタスクを始める確率が下がった**という変化でした。

## 「次に何を作るか」も任せやすくなった

Repositoryの現在地点をAI自身が確認できるようになると、もう一段任せられることが増えました。

「この関数を書いて」ではなく、

> 今のRepositoryを見て、次にやるべきタスクを選んで

と頼めるようになります。

自分の場合は、未完了Issueだけでなく、最近マージされたPRのNext phase、TODO、Docsと実装の差、テスト不足、Security、UXあたりも見てもらっています。

もちろん、AIが選んだタスクを何でもそのまま実装するわけではありません。

ただ、「次に何をするか」を決める前の調査をかなり任せられるようになりました。

以前は、

```text
自分がRepositoryを思い出す
        ↓
自分が次タスクを決める
        ↓
AIに実装を頼む
```

という流れでした。

今は、かなりこうなっています。

```text
Repository
   ↓
AIが現在地点を確認
   ↓
候補タスクを整理
   ↓
次の変更を選ぶ
   ↓
実装
   ↓
Test / CI / Review
   ↓
PR
   ↓
Repository
```

このループが回るようになったことで、AIの役割が「コードを書く人」から少し広がりました。

## コードを書いて終わりにしない

Repositoryを正本にするなら、実装結果もRepositoryに戻っていないと意味がありません。

なので、自分の中では「コードが書けた」だけでは完了扱いにしないようにしています。

HertaのCIでは現在、Format / Lint / Typecheck / Test / Buildに加えて、Production Composeの検証、Production Docker Build、runtime verification、CycloneDX SBOMの生成、Grypeによる脆弱性scanまで行っています。

AIにも、可能な範囲でそこまで確認させます。

```text
調査
 ↓
実装
 ↓
Test
 ↓
CI
 ↓
セルフレビュー
 ↓
PR
```

実行できなかったものがあれば「未実行」として残す。

これも地味ですが大事でした。

「実装しました」と言われたコードがmainに入るまでの間には、まだ結構やることがあります。

## Repositoryだけで全部解決するわけではない

Repository is the Source of Truthと言いつつ、全部を1か所へ押し込めているわけではありません。

今のところ、自分の中では役割をだいたいこう分けています。

- Repository: 今、何が実装されているか
- Issue: 何を解決したいか、これから何をしたいか
- PR: なぜその変更をしたか
- Docs: どう動くか、どう運用するか
- Notion: 次のチャットや作業へ渡す引き継ぎ
- 会話: その場で考えていることや相談

Notionには「ここまで進んだ」「次はこれを見る」という情報を残します。

でも、数日後に作業を再開するときは、その情報をそのまま事実として使わず、もう一度GitHubを見ます。

実際、この記事を書いている最中にもHertaのmainは更新されていました。

引き継ぎ資料を書いた時点のlatest commitと、記事を書くために確認した時点のlatest commitがもう違います。

こういうことが普通に起きるので、静的な引き継ぎ文だけをSource of Truthにしない方が自分には合っていました。

## 個人開発で一番効いたのは、実装速度より「再開しやすさ」だった

AI開発というと、「コードを書く速度が何倍になった」みたいな話になりがちです。

もちろん、それも便利です。

でも自分の場合、思った以上に大きかったのは別のところでした。

**数日空いたあとでも、Repositoryから現在地点を復元しやすくなったことです。**

個人開発では、実装以外も全部自分でやります。

設計を考えて、Issueを見て、CIを直して、別のRepositoryへ移動して、また戻ってくる。

そのとき毎回、

> これどこまでやったっけ？

から始めるのが意外と重い。

今はAIに、

> main、最近のPR、Issue、Docs、Testsを確認して現在地点を整理して

と頼むことで、かなり早く戻れるようになりました。

個人的には、コード生成そのものより、このコンテキスト復元コストが下がったことの方が長期の個人開発では効いています。

## まだ人間側に残していること

もちろん、全部を自動で進めているわけではありません。

プロダクトの方向性、大きな設計変更、本番環境に影響する操作、Secretや権限まわり、最終的なPRのマージ判断などは、人間側に残しています。

特に「Repositoryを読める」と「何をしてもいい」は別です。

AIが次タスクを選べるようになっても、Productionの変更や破壊的な操作まで勝手に進めさせる必要はありません。

自分がやりたいのは完全放置の自律開発ではなく、

> Repositoryを見れば、AIも人間も同じ現在地点から話を始められる

状態に近いです。

## まとめ

最初は、AIにもっと長いプロンプトを書けば開発が安定すると思っていました。

でも長く続けてみると、問題はプロンプトの詳しさだけではありませんでした。

そのプロンプトに書かれた「現在」が、すぐ過去になる。

Issueも古くなる。READMEも古くなる。自分の記憶も普通に抜けます。

そこで現在状態を全部AIへ教えるのではなく、

> まずRepositoryを見て、現在状態を自分で確認する

というルールに変えました。

それだけで、既存機能をもう一度作りそうになることが減って、次タスクの調査も任せやすくなり、数日ぶりに開発へ戻るときも楽になりました。

少なくとも今の自分の個人開発では、AIに何を覚えさせるかより、**何を見れば正しい状態に戻れるかを決めておくこと**の方が大事だったように思います。

AIにコードを書いてもらうところから始めましたが、最近は少しずつ、AIと一緒にRepositoryを育てている感じに変わってきました。

まだ運用自体も試行錯誤中なので、この先また変わるかもしれません。

でも「Repository is the Source of Truth」は、今のところかなり残りそうなルールです。

## 関連・参考資料

今回の運用と近い考え方や、AIコーディングエージェントへRepositoryのコンテキストを渡す方法を考えるうえで参考になる公開資料です。

- [リポジトリこそがSSOTであり、コンテキストである](https://zenn.dev/gyu07/articles/ff7613864b23bc)
  - Repositoryそのものをコーディングエージェントの現在コンテキストとして捉える、かなり近いテーマの記事です。
- [Context Engineering for Coding Agents - Martin Fowler](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html)
  - コーディングエージェントに「何を見せるか」を設計するContext Engineeringについて整理されています。
- [AIに毎回プロジェクトを説明するのをやめる — AGENTS.mdで、コーディングエージェントに「リポジトリの歩き方」を1枚で渡す実践ガイド - Qiita](https://qiita.com/akira_papa_AI/items/3fd7d14fc53d13a27f4a)
  - Repository内にエージェント向けのルールを置き、毎回同じ説明をしない運用の実践例です。
- [Adding repository custom instructions for GitHub Copilot in your IDE - GitHub Docs](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide/add-repository-instructions-in-your-ide?tool=vscode)
  - Repository-wide instructionsやAGENTS.mdなど、Repository固有のコンテキストをAIへ渡す公式ドキュメントです。
