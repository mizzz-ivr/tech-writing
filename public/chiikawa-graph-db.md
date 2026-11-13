---
title: ちいかわの相関図をDBに入れたら、Graph DBを使う理由がちょっと分かった
tags:
  - Neo4j
  - GraphDB
  - データベース
  - TypeScript
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

ちいかわのキャラクター相関図みたいなものをDBに入れようとした。

最初は普通にRDBでいいと思っていた。

```text
characters
relationships
```

2テーブル。

終わり。

……と思った。

でも、

> ちいかわと直接つながっているキャラは？

なら簡単なのに、

> うさぎから2人以内でたどり着けるキャラは？

> ちいかわとモモンガの共通のつながりは？

> この2人を最短でつなぐと、誰を経由する？

みたいな質問を考え始めると、急にSQLが「相関図を表現している」というより、**表に押し込んだ関係を頑張ってたどっている**感じになってきた。

そこでNeo4jのGraph DBを見てみた。

```text
(ちいかわ) ── FRIENDS_WITH ── (ハチワレ)
    │
    └──── FRIENDS_WITH ───── (うさぎ)
```

……そのままだ。

この記事では、ちいかわのキャラクターを題材に、

**RDBでも持てる関係データを、なぜわざわざGraph DBで持つことがあるのか**

を考えてみる。

> ※記事中のキャラクター間Relationshipは、Graph DBを説明するために単純化したサンプルです。公式の相関図・設定を定義するものではありません。

---

## 最初はPostgreSQLで普通にいけると思った

まずキャラクター。

```sql
CREATE TABLE characters (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);
```

そして関係。

```sql
CREATE TABLE character_relationships (
  from_character_id UUID NOT NULL,
  to_character_id UUID NOT NULL,
  relationship_type TEXT NOT NULL,

  PRIMARY KEY (
    from_character_id,
    to_character_id,
    relationship_type
  )
);
```

これで、

```text
ちいかわ
ハチワレ
うさぎ
モモンガ
くりまんじゅう
シーサー
ラッコ
```

を入れる。

Relationshipも記事用に単純化して、

```text
ちいかわ ─ FRIENDS_WITH ─ ハチワレ
ちいかわ ─ FRIENDS_WITH ─ うさぎ
ハチワレ ─ FRIENDS_WITH ─ うさぎ
```

みたいに入れる。

ここまでは何も困らない。

むしろRDBで十分。

---

## 「ちいかわの友達は？」も簡単

直接つながっているキャラクターを出すだけなら、普通のJOINでいい。

```sql
SELECT c.name
FROM character_relationships r
JOIN characters c
  ON c.id = r.to_character_id
WHERE r.from_character_id = :chiikawa_id
  AND r.relationship_type = 'FRIENDS_WITH';
```

分かりやすい。

速くするならindexも貼れる。

```sql
CREATE INDEX idx_character_relationships_from
ON character_relationships (
  from_character_id,
  relationship_type
);
```

ここでGraph DBを持ち出す必要は全然ない。

自分：

> やっぱPostgreSQLでよくない？

となった。

---

## 「友達の友達」を聞き始めた

次。

> ちいかわと直接つながっているキャラだけじゃなく、そのキャラとつながっているキャラまで見たい。

つまり、

```text
ちいかわ
  ↓
1 hop
  ↓
誰か
  ↓
2 hop
  ↓
誰か
```

を取りたい。

固定で2階層ならJOINを増やせる。

```sql
SELECT DISTINCT c2.name
FROM character_relationships r1
JOIN character_relationships r2
  ON r1.to_character_id = r2.from_character_id
JOIN characters c2
  ON c2.id = r2.to_character_id
WHERE r1.from_character_id = :chiikawa_id;
```

まだいける。

じゃあ3階層。

4階層。

「何階層か分からないけど、つながっているところまで」。

ここから再帰CTEが見えてくる。

```sql
WITH RECURSIVE connections AS (
  SELECT
    from_character_id,
    to_character_id,
    1 AS depth
  FROM character_relationships
  WHERE from_character_id = :start_id

  UNION ALL

  SELECT
    r.from_character_id,
    r.to_character_id,
    c.depth + 1
  FROM character_relationships r
  JOIN connections c
    ON r.from_character_id = c.to_character_id
  WHERE c.depth < 3
)
SELECT DISTINCT
  ch.name,
  connections.depth
FROM connections
JOIN characters ch
  ON ch.id = connections.to_character_id;
```

書ける。

PostgreSQLは普通に強い。

でも、自分がやりたいことを日本語に戻すと、

> このキャラから関係をたどって3hop以内を出して

だった。

SQLを見たとき、

**質問より実装の方がだいぶ重い。**

ここでGraph DBが少し気になってきた。

---

## Neo4jだと「キャラ」と「関係」がそのまま出てくる

Neo4jのProperty Graphでは、ざっくり、

```text
Node
Relationship
Property
```

でデータを表現する。

キャラクターはNode。

```text
(:Character {name: "ちいかわ"})
```

キャラクター同士の関係はRelationship。

```text
(:Character)-[:FRIENDS_WITH]->(:Character)
```

図にすると、そのまま。

```text
(ちいかわ)
    |
 FRIENDS_WITH
    |
(ハチワレ)
```

この時点でかなり分かりやすい。

---

## Cypherでサンプルを作ってみる

Neo4jのQuery LanguageであるCypherなら、例えばこんな感じ。

```cypher
MERGE (chiikawa:Character {name: "ちいかわ"})
MERGE (hachiware:Character {name: "ハチワレ"})
MERGE (usagi:Character {name: "うさぎ"})
MERGE (momonga:Character {name: "モモンガ"})
MERGE (kurimanju:Character {name: "くりまんじゅう"})
MERGE (shisa:Character {name: "シーサー"})
MERGE (rakko:Character {name: "ラッコ"})
```

Relationshipも作る。

```cypher
MATCH (c:Character {name: "ちいかわ"})
MATCH (h:Character {name: "ハチワレ"})
MATCH (u:Character {name: "うさぎ"})

MERGE (c)-[:FRIENDS_WITH]->(h)
MERGE (c)-[:FRIENDS_WITH]->(u)
MERGE (h)-[:FRIENDS_WITH]->(u)
```

> ※ここでのRelationshipは記事用サンプルです。

---

## 「ちいかわと直接つながってるキャラは？」

Cypherだとこう。

```cypher
MATCH (:Character {name: "ちいかわ"})
  -[:FRIENDS_WITH]-
  (friend:Character)
RETURN friend.name
```

かなり読める。

```text
ちいかわ
 ↓ FRIENDS_WITH
誰？
```

が、そのままQueryになっている感じ。

---

## 「2hop以内」はもっとGraphっぽい

例えば、

> ちいかわからFRIENDS_WITHを最大2回たどれるキャラクター

なら、

```cypher
MATCH
  (:Character {name: "ちいかわ"})
  -[:FRIENDS_WITH*1..2]-
  (related:Character)
RETURN DISTINCT related.name
```

で表現できる。

ここで、

```text
*1..2
```

がかなりGraphっぽい。

1〜2回Relationshipをたどる。

RDBでもできる。

でもGraph DBだと、**Traversal自体がQueryの主役**になっている。

自分がGraph DBを見て初めて「なるほど」と思ったのはここだった。

---

## 相関図で本当に聞きたいことは「行」じゃなく「経路」だった

相関図を見ていて聞きたくなるのは、

```text
キャラクター一覧ください
```

だけじゃない。

むしろ、

```text
AとBはどうつながっている？

AとBの共通の知り合いは？

AからBへ何人経由する？

Aの周辺に誰が集まっている？

どのキャラクターが一番いろんなキャラとつながっている？
```

みたいな質問。

つまり欲しいのが、

```text
Row
```

より、

```text
Path
```

になっている。

Neo4jではPathも自然に扱える。

例えば最短経路。

```cypher
MATCH
  (a:Character {name: "ちいかわ"}),
  (b:Character {name: "モモンガ"}),
  p = shortestPath((a)-[*]-(b))
RETURN p
```

これがかなり直感的。

---

## 共通のつながりも書きやすい

例えば、

> ちいかわとハチワレの両方につながっているキャラクターは？

記事用の単純化したGraphなら、

```cypher
MATCH
  (:Character {name: "ちいかわ"})--(common:Character),
  (:Character {name: "ハチワレ"})--(common)
RETURN DISTINCT common.name
```

で探せる。

GraphのPatternをそのままQueryにする。

ここまで来ると、

**「相関図を検索している」感がかなり強い。**

---

## Relationshipにもデータを持たせられる

さらに面白いのが、Relationship自体にもPropertyを持てること。

例えば記事用のデータベースなら、

```cypher
MATCH
  (a:Character {name: "ちいかわ"}),
  (b:Character {name: "ハチワレ"})

MERGE (a)-[r:RELATED_TO]->(b)
SET
  r.kind = "friend",
  r.source = "sample",
  r.checkedAt = date("2026-09-29")
```

みたいにできる。

ただ、

```text
source
checkedAt
```

が1件だけならいいけど、根拠が何話分も増えるならRelationship Propertyだけでは足りなくなる。

その場合は、

```text
Character
   ↓
Relationship
   ↓
Evidence
```

みたいにEvidence自体をNodeにする設計も考えられる。

Graph DBにすると何でも雑に矢印でつなげばいい、という話でもない。

---

## 「友達」「同僚」「師弟」……Relationship Typeが増殖しない？

Graphにして楽しくなってくると、

```text
FRIENDS_WITH
WORKS_WITH
TEACHES
LIKES
KNOWS
LIVES_NEAR
APPEARS_WITH
```

みたいに何でもRelationship Typeにしたくなる。

これも少し怖い。

最初から何十種類も作ると、Queryを書く側も扱いづらくなる。

なので実際に作るなら、

```text
FRIENDS_WITH
WORKS_WITH
MENTORS
RELATED_TO
```

くらいのCanonicalなRelationship Typeをまず決める。

細かい分類はPropertyに逃がす。

```text
(:Character)
  -[:RELATED_TO {kind: "..."}]->
(:Character)
```

という設計も候補になる。

**GraphだからSchemaを考えなくていい、ではない。**

むしろ「何をNodeにして、何をRelationshipにするか」が設計そのものになる。

---

## じゃあRDBは向いてないの？

ここはかなり大事。

**全然そんなことはない。**

ちいかわキャラクターDBを作るとして、主な機能が、

- 名前で検索
- キャラクター詳細表示
- 登場情報一覧
- お気に入り登録
- 管理画面からCRUD

くらいなら、自分なら普通にPostgreSQLを選ぶと思う。

理由は単純。

楽だから。

既存のWeb FrameworkやORMともつなぎやすい。

Transactionも扱いやすい。

JOINで十分な範囲なら、わざわざDatabaseを増やしたくない。

Graph DBが面白くなるのは、

**Relationship TraversalそのものがProductの主要機能になったとき。**

例えば、

> このキャラクターとこのキャラクターはどうつながってる？

> 3hop以内の関連キャラを出して

> 共通のつながりが多いキャラを探して

> 相関図そのものを検索したい

みたいなQueryが中心になる場合。

ここならNeo4jを使う理由が見えてくる。

---

## 「データがGraphっぽい」だけでは理由にならなかった

最初は、

> 相関図なんだからGraph DBでしょ

と思いそうになった。

でも考えてみると、

RDBだってRelationship Tableを作れば普通に保存できる。

重要なのはデータの見た目ではなかった。

```text
保存したいもの
```

より、

```text
何を問い合わせたいか
```

だった。

例えば、

### RDB寄り

```text
キャラクター詳細を表示したい
名前で検索したい
一覧をページングしたい
管理画面で編集したい
```

### Graph DB寄り

```text
関係を何段もたどりたい
最短経路を知りたい
共通のつながりを探したい
Relationship Patternを検索したい
```

同じ「ちいかわキャラクターDB」でも、欲しいQueryで選択が変わる。

---

## 実際に作るならHybridもありそう

ここまで考えて、

> PostgreSQLかNeo4jか、どっちか選ばないといけないの？

となる。

別にそんなこともない。

例えば、

```text
PostgreSQL
├─ Character基本情報
├─ User
├─ Favorite
└─ 管理系データ

Neo4j
└─ Character Relationship Graph
```

みたいに役割を分けることもできる。

ただ、個人開発で最初からDBを2種類運用するのは普通に面倒。

同期も必要。

障害点も増える。

バックアップも2系統。

なので自分なら、

1. まずPostgreSQLで作る
2. Relationship Queryが本当に苦しくなったか見る
3. Graph Traversalが主要機能になったらNeo4jを検討する

くらいにする。

Graph DBを使いたいからGraph DBを入れるのではなく、

**SQLでRelationship Traversalを書くことがProductの複雑さになったら入れる。**

その順番がよさそう。

---

## 今回は性能比較まではしていない

ここは明確にしておく。

今回はNeo4jの公式ドキュメントにあるProperty Graph / Cypherの考え方を確認しながら、ちいかわ相関図を題材にデータモデルとQueryを組んでいる。

PostgreSQLとNeo4jに同じ大量データを入れて、

```text
10万Node
100万Relationship
3hop query
p95 latency
```

みたいなBenchmarkはしていない。

なので、

> Neo4jの方が速い

とはこの記事では言わない。

Graph DBを使う理由として今回感じたのは、速度より先に、

**関係と経路をQueryの中心に置けること。**

そこだった。

---

## まとめ

ちいかわの相関図をDBへ入れたい。

最初：

> charactersとrelationshipsの2テーブルで終わりでは？

直接の関係を取る：

> 普通にJOINでいける。

友達の友達：

> JOIN増やせばいける。

3hop：

> 再帰CTEか。

最短経路：

> ……相関図を調べたいだけなんだけどな。

Neo4jを見る。

```cypher
MATCH
  (:Character {name: "ちいかわ"})
  -[:FRIENDS_WITH*1..2]-
  (related)
RETURN related
```

自分：

> **あ、Graphを検索してる。**

となった。

ちいかわの相関図だからGraph DBが正解、という話ではない。

RDBでも普通に保存できる。

CRUD中心ならPostgreSQLの方が自分には扱いやすい。

でも、

**「誰と誰が、どうつながっている？」がProductの中心になった瞬間、Graph DBの設計が急に自然に見える。**

今回一番腑に落ちたのはそこだった。

DBを選ぶとき、

> このデータは何っぽい？

ではなく、

> このデータに、どんな質問を一番たくさんする？

から考える。

ちいかわの相関図を作ろうとして、Graph DBの使いどころがちょっと分かった。

---

## 参考

- [ちいかわ公式総合情報サイト](https://chiikawa-info.jp/)
- [Neo4j - What is a graph database](https://neo4j.com/docs/getting-started/graph-database/)
