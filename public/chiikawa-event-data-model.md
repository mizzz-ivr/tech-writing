---
title: ちいかわPOP UP STOREをDBに入れようとしたら、「イベント」って思ったより難しかった
tags:
  - TypeScript
  - DB設計
  - データモデリング
  - 個人開発
  - ちいかわ
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

ちいかわのイベント情報を見ていた。

2026年9月29日時点。

- JR池袋駅のPOP UP STORE → 9月28日で終了
- グランデュオ蒲田 → 9月30日まで開催
- JR仙台駅 → 10月1日から開催

自分：

> 池袋は昨日終わった。
> 蒲田は明日まで。
> 仙台は明後日から。

……これ、DBに入れるならどう持つんだ？

最初はこう思っていた。

```ts
type Event = {
  name: string;
  place: string;
  startDate: string;
  endDate: string;
  status: "upcoming" | "ongoing" | "ended";
};
```

これで終わり。

のはずだった。

でも実際のイベント一覧を見ると、

- 同じ「ちいかわPOP UP STORE」が全国で何回も開催される
- 会場ごとに期間が違う
- 終了日はあるものも、まだ決まっていないものもある
- 「開催中」は今日の日付で勝手に変わる
- 中止・延期・早期終了みたいな例外も考えたい
- 元情報が更新された日時も残したい

と、だんだん面倒になってきた。

**「イベント情報を保存する」だけなのに、意外とデータ設計の論点が多い。**

今回は、ちいかわPOP UP STOREを題材に、

> イベント情報ってどう持つと後から困りにくいんだろう？

を考えてみる。

---

## まず「開催中」をDBに入れたくなった

最初に作りたくなったのはこれ。

```ts
type EventStatus =
  | "upcoming"
  | "ongoing"
  | "ended";

type Event = {
  name: string;
  venue: string;
  startDate: string;
  endDate: string;
  status: EventStatus;
};
```

例えばこんなデータ。

```ts
const event = {
  name: "ちいかわPOP UP STORE",
  venue: "グランデュオ蒲田",
  startDate: "2026-09-08",
  endDate: "2026-09-30",
  status: "ongoing",
};
```

2026年9月29日に見るなら正しい。

でも翌日もまだ正しい。

その次の日。

2026年10月1日。

```ts
status: "ongoing"
```

……嘘になる。

日付は変わったのに、DBは勝手に変わってくれない。

そこで気づいた。

**「開催中」は保存する値ではなく、日付から計算できる値では？**

---

## statusを消してみる

一旦こうする。

```ts
type Event = {
  name: string;
  venue: string;
  startDate: string;
  endDate: string | null;
};
```

そして表示するときに判定する。

```ts
type EventStatus =
  | "upcoming"
  | "ongoing"
  | "ended";

function getEventStatus(
  startDate: string,
  endDate: string | null,
  today: string,
): EventStatus {
  if (today < startDate) {
    return "upcoming";
  }

  if (endDate !== null && today > endDate) {
    return "ended";
  }

  return "ongoing";
}
```

ISO形式の `YYYY-MM-DD` に揃えている前提なら、日付だけの比較は文字列でも順序を保てる。

2026年9月29日を入れてみる。

```ts
const today = "2026-09-29";

getEventStatus(
  "2026-09-18",
  "2026-09-28",
  today,
);
// ended

getEventStatus(
  "2026-09-08",
  "2026-09-30",
  today,
);
// ongoing

getEventStatus(
  "2026-10-01",
  "2026-10-09",
  today,
);
// upcoming
```

かなり自然。

```text
JR池袋駅
→ ended

グランデュオ蒲田
→ ongoing

JR仙台駅
→ upcoming
```

「開催中」という文字を毎日更新しなくていい。

**事実として保存するのは期間。状態はそこから導出する。**

この方がDBとして扱いやすい。

---

## でも「ちいかわPOP UP STORE」が何十個もできる

次に気になった。

公式一覧を見ると、

```text
ちいかわPOP UP STORE
├─ JR池袋駅
├─ グランデュオ蒲田
├─ 中部国際空港
├─ JR仙台駅
├─ 青森ELM
├─ 町田モディ
└─ ...
```

みたいになっている。

全部イベントではある。

でも全部の `name` に、

```text
ちいかわPOP UP STORE
```

を入れていくのは、ちょっと違和感がある。

ここで、

**「企画そのもの」と「各会場での開催」は別物では？**

となった。

---

## EventとOccurrenceを分ける

そこで2つに分けてみる。

```ts
type EventSeries = {
  id: string;
  title: string;
  sourceUrl: string;
};

type EventOccurrence = {
  id: string;
  seriesId: string;
  venueName: string;
  startDate: string;
  endDate: string | null;
};
```

例えば、

```ts
const series: EventSeries = {
  id: "chiikawa-pop-up-store",
  title: "ちいかわPOP UP STORE",
  sourceUrl: "https://chiikawa-info.jp/pus.html",
};
```

開催場所は別。

```ts
const occurrences: EventOccurrence[] = [
  {
    id: "ikebukuro-2026-09",
    seriesId: "chiikawa-pop-up-store",
    venueName: "JR池袋駅",
    startDate: "2026-09-18",
    endDate: "2026-09-28",
  },
  {
    id: "kamata-2026-09",
    seriesId: "chiikawa-pop-up-store",
    venueName: "グランデュオ蒲田",
    startDate: "2026-09-08",
    endDate: "2026-09-30",
  },
  {
    id: "sendai-2026-10",
    seriesId: "chiikawa-pop-up-store",
    venueName: "JR仙台駅",
    startDate: "2026-10-01",
    endDate: "2026-10-09",
  },
];
```

こうすると、

```text
EventSeries
「ちいかわPOP UP STORE」
        │
        ├── EventOccurrence: JR池袋駅
        ├── EventOccurrence: グランデュオ蒲田
        └── EventOccurrence: JR仙台駅
```

になる。

同じ企画名を何十回も複製しなくていい。

企画そのものの説明や公式URLも1か所に寄せられる。

これ、ちいかわじゃなくても、

- 全国ツアー
- 展覧会
- ポップアップショップ
- ライブ
- 期間限定カフェ
- スポーツの試合

みたいな情報を扱うときに普通に使えそう。

---

## 「終了日未定」が出てきた

イベント一覧を見ていると、開始日だけ書かれているものもある。

例えば、

```text
2026年8月21日(金)～
```

のような形式。

最初、

```ts
endDate: ""
```

でいいかと思った。

でも空文字は嫌だ。

```text
終了日がない
```

のと、

```text
終了日がまだ分からない
```

の意味が曖昧になる。

なので少なくとも、

```ts
endDate: string | null;
```

にした方が扱いやすい。

```ts
{
  startDate: "2026-08-21",
  endDate: null,
}
```

そして `endDate === null` なら、開始済みの場合は基本的にongoingとして扱う。

ただし、これだけだと新しい問題が出る。

---

## 日付だけでは表せない「終了」がある

例えばイベントが何らかの事情で予定より早く終了したとする。

DBには、

```text
startDate = 2026-09-01
endDate   = 2026-10-01
```

が入っている。

でも実際には9月20日で終了した。

9月25日に日付だけで判定すると、

```text
ongoing
```

になってしまう。

そこで例外だけ別に持つ。

```ts
type EventStatusOverride =
  | "cancelled"
  | "postponed"
  | "ended";

type EventOccurrence = {
  id: string;
  seriesId: string;
  venueName: string;
  startDate: string;
  endDate: string | null;
  statusOverride: EventStatusOverride | null;
};
```

通常状態は日付から導出する。

特殊状態だけ保存する。

```ts
function getEventStatus(
  event: EventOccurrence,
  today: string,
) {
  if (event.statusOverride !== null) {
    return event.statusOverride;
  }

  if (today < event.startDate) {
    return "upcoming";
  }

  if (
    event.endDate !== null &&
    today > event.endDate
  ) {
    return "ended";
  }

  return "ongoing";
}
```

これなら、

```text
通常
→ 日付がSource of Truth

例外
→ statusOverrideがSource of Truth
```

にできる。

個人的にはこの形がかなり好き。

---

## 「終了」を保存しないのに、公式の「終了」は無視していい？

ここで少しややこしい。

公式ページには、すでに終了した会場へ

```text
【終了】
```

と表示されている。

じゃあそれをそのまま `status = ended` として保存した方が正確では？

という考え方もある。

自分なら、公式側の状態も捨てずに別で持つ。

```ts
type SourceStatus =
  | "active"
  | "ended"
  | "unknown";

type EventOccurrence = {
  // ...
  sourceStatus: SourceStatus;
};
```

そしてアプリ上の表示状態とは分ける。

```text
sourceStatus
→ 元サイトがどう表現していたか

computedStatus
→ 自分のシステムが日付からどう判断したか
```

この2つが食い違ったら、

> 公式情報が更新された？
> 日付データが間違っている？
> 早期終了した？

と気づける。

**外部データを取り込むなら、「元データの事実」と「自分の解釈」を分ける。**

ちいかわを見ていたはずなのに、だいぶデータパイプラインっぽくなってきた。

---

## sourceUrlだけじゃなく「いつ確認したか」も欲しくなった

イベント情報は変わる。

会期延長。

開催時間変更。

会場変更。

中止。

公式ページが更新されたとき、

DBに入っている情報がいつの時点のものなのか分からないと困る。

なので、

```ts
type EventOccurrence = {
  id: string;
  seriesId: string;
  venueName: string;
  startDate: string;
  endDate: string | null;

  sourceUrl: string;
  sourceCheckedAt: string;
};
```

も欲しい。

例えば、

```ts
{
  sourceUrl: "https://chiikawa-info.jp/pus.html",
  sourceCheckedAt: "2026-09-29T17:00:00+09:00",
}
```

これがあれば、

> これ、いつ確認したデータ？

が分かる。

地味。

でも運用を始めるとかなり大事。

---

## 最終的にこうなった

最初。

```ts
type Event = {
  name: string;
  place: string;
  startDate: string;
  endDate: string;
  status: "ongoing" | "ended";
};
```

だった。

最終的にはこんな感じになった。

```ts
type EventSeries = {
  id: string;
  title: string;
  sourceUrl: string;
};

type EventStatusOverride =
  | "cancelled"
  | "postponed"
  | "ended";

type SourceStatus =
  | "active"
  | "ended"
  | "unknown";

type EventOccurrence = {
  id: string;
  seriesId: string;

  venueName: string;

  startDate: string;
  endDate: string | null;

  statusOverride: EventStatusOverride | null;
  sourceStatus: SourceStatus;

  sourceUrl: string;
  sourceCheckedAt: string;
};
```

そして、

```text
開催予定
開催中
終了
```

は基本的に表示時に計算する。

---

## これなら「今日やってるちいかわイベント」も出せる

ここまで持てれば、やりたかったことはかなり簡単になる。

```ts
const activeEvents = occurrences.filter(
  (event) =>
    getEventStatus(event, "2026-09-29")
      === "ongoing",
);
```

あとは場所や距離を持たせれば、

```text
今日開催中
   ↓
東京都内
   ↓
終了日が近い順
```

みたいな検索もできる。

例えば、

> 明日で終わるちいかわイベントある？

も作れる。

通知までつけるなら、

```text
終了3日前
↓
まだ行ってない
↓
通知
```

みたいなこともできる。

最初は、

> ちいかわのイベントを一覧で見たい

だけだった。

気づいたら、

```text
Event Series
Occurrence
Derived State
Override
Source Verification
```

まで考えていた。

---

## スクレイピングまでは今回やらない

今回のサンプルデータは、ちいかわ公式情報サイトに掲載されているイベント情報を確認して作っている。

自動クローラーやスクレイピング処理までは実装していない。

そこまでやるなら、

- robots.txt
- 利用規約
- アクセス頻度
- HTML変更への耐性
- 重複取り込み
- 差分更新
- 公式情報削除時の扱い

まで別の問題になる。

なので今回は、

**取得方法ではなく、取得した後どう持つか。**

ここに絞った。

---

## まとめ

ちいかわPOP UP STOREをDBに入れようとした。

最初：

> 名前・場所・開始日・終了日・statusでよくない？

数分後：

> 「開催中」って保存する必要ある？

さらに見る：

> 同じPOP UP STOREが全国にある。

考える：

> EventとOccurrence分ける？

終了日を見る：

> null必要じゃん。

例外を考える：

> cancelledもいる。

公式情報を見る：

> Source側のstatusも残したい。

最後：

```text
ちいかわ
  ↓
POP UP STORE
  ↓
DB設計
  ↓
Derived State
  ↓
Source of Truth
```

**ちいかわを追っていたはずなのに、いつの間にかデータモデリングの話になっていた。**

でもこういう題材の方が、個人的には設計を考えやすい。

架空の「イベントA」「イベントB」より、

> 池袋は昨日終わった。
> 蒲田は明日まで。
> 仙台は明後日から。

の方が、なぜstatusを計算したくなるのか直感的に分かる。

イベント情報を扱うなら、

- 変わらない事実は保存する
- 今日によって変わる状態はできるだけ導出する
- 繰り返す企画と個別開催を分ける
- 例外だけ明示的に上書きする
- 外部情報ならSourceと確認日時を残す

あたりを最初に考えておくと、後からかなり楽になりそう。

ちいかわ、かわいい。

データ設計は、思ったよりかわいくなかった。

---

## 参考

- [ちいかわPOP UP STORE｜ちいかわ公式総合情報サイト](https://chiikawa-info.jp/pus.html)
