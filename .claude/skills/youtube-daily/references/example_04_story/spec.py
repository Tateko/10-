import json
L=json.load(open("lines.json"))
SRC={"1":"本人のX（2026/2/10）","2":"本人のX（2026/2/26）","3":"本人のX（2026/3/11）","4":"本人のX（2026/3/14）","5":"本人のX（2026/5/19）",
     "6":"本人のX（2026/6/10）","7":"本人のX（2026/8/7）","8":"本人のX（2026/10/24）","9":"Bullet Point Podcast（2026/5/24）",
     "10":"App Store の Pep AI","11":"Starter Story","12":"MRRstory"}
# (行数, 型, 中身)。A＝絵（img・year・head）、B＝図解（kind・title・sub・items・note）
S=[
 (3,"A",dict(img=1,year="2026年10月24日",head=["8か月で、","70万ドル。"])),
 (3,"B",dict(kind="boxes",title="この動画で追う3つの出来事",sub="コード経験ゼロの学生が、AIで作ったアプリの8か月",items=["コード経験ゼロ","3万ドルの賭け","集客の柱が壊れる"],hi=2)),
 (2,"A",dict(img=3,year="2026年",head=["どうやって、","立て直した？"])),
 (2,"B",dict(kind="boxes",title="この動画の数字について",sub="くわしくは「光と影」の章と説明欄で",items=["本人が公開した記録のまま","円は1ドル＝150円で計算"])),
 (2,"A",dict(img=5,year="2026年",head=["ビジネスを学ぶ","大学生。"])),
 (4,"B",dict(kind="timeline",title="コード経験ゼロから、3つ目のアプリへ",sub="本人のXの投稿から",items=[["2025年11月ごろ","コード経験ゼロ"],["2026年2月10日","「3つ目のアプリを出す」"],["2026年2月","Pep AI を公開"]])),
 (2,"A",dict(img=7,year="2026年2月",head=["3つ目のアプリ、","Pep AI。"])),
 (2,"B",dict(kind="steps",title="Pep AI でできること",sub="App Store の説明から",items=["使った物を記録","体調を記録","通知で知らせる"],note="説明には「医療の助言はしません」とある。この動画は事業の数字だけを追う")),
 (2,"A",dict(img=9,year="2026年",head=["創業者は2人、","社員はゼロ。"])),
 (5,"B",dict(kind="icons",title="作る前に、人が集まっていた",sub="ポッドキャストと紹介記事から",items=["順番待ち 300人","最初の100人","1つのRedditの投稿"],note="Reddit＝海外の大きな掲示板")),
 (2,"A",dict(img=11,year="2026年",head=["人を見つけてから、","作る。"])),
 (3,"B",dict(kind="big",title="インフルエンサーに使ったお金",sub="紹介記事（MRRstory）による",big="3万ドル",bigsub="約450万円",items=["TikTok","Instagram","YouTube"])),
 (2,"A",dict(img=13,year="2026年",head=["学生には、","大きな賭け。"])),
 (3,"B",dict(kind="compare",title="使ったお金と、その月の売上",sub="紹介記事（MRRstory）による",items=[["使ったお金","3万ドル"],["その月の売上","約6万ドル"]],note="使ったお金の約2倍。これが、いちばんの集客の柱になっていく")),
 (3,"A",dict(img=15,year="2026年2月26日",head=["利用者は、","500人。"])),
 (3,"B",dict(kind="quote",title="公開から18日",sub="本人のX（2026/3/11）",big="「たった18日で、売上が1万ドルに届いた」",bigsub="約150万円")),
 (4,"A",dict(img=17,year="2026年3月14日",head=["3日後、","4,900ダウンロード。"])),
 (3,"B",dict(kind="table",title="2026年3月14日の数字",sub="本人のXの投稿から",items=[["ダウンロード","4,900回以上"],["売上","14,686ドル"],["毎月の定期収入","2,716ドル"],["値段（アメリカ）","月9.99ドル・年29.99ドル"]],note="毎月の定期収入＝毎月決まって入ってくる売上")),
 (2,"A",dict(img=19,year="2026年5月",head=["約7週間で、","5万1千ドル。"])),
 (5,"B",dict(kind="timeline",title="売上は、どこまで伸びたか",sub="本人のXの投稿から（種類の違う数字に注意）",items=[["5月9日","売上の合計 10万ドル"],["5月19日","直近28日で 6万ドル"],["6月10日","売上の合計 20万ドル"]])),
 (3,"A",dict(img=21,year="2026年6月10日",head=["20万ドル。","その裏で——"])),
 (2,"B",dict(kind="quote",title="10月24日の振り返り",sub="本人のX（2026/10/24）",big="「いちばんの集客の手段が、ほぼ壊れた」",bigsub="")),
 (2,"A",dict(img=23,year="8か月の途中",head=["インフルエンサーの","投稿が制限。"])),
 (3,"B",dict(kind="compare",title="柱が1本、倒れた",sub="本人のXと紹介記事から",items=[["これまで","インフルエンサーの紹介"],["制限のあと","人を連れてくる道が細く"]],note="最初に3万ドルを使った、あの方法")),
 (2,"A",dict(img=25,year="8か月の途中",head=["次の道は、","Meta広告。"])),
 (3,"B",dict(kind="steps",title="集客の切り替え",sub="Meta＝FacebookやInstagramを運営する会社",items=["人に紹介を頼む","自分で広告を出す","自分で動かせる集客"],hi=2)),
 (3,"A",dict(img=27,year="2026年8月7日",head=["10万","ダウンロード。"])),
 (4,"B",dict(kind="timeline",title="売上の合計",sub="本人のXの投稿から",items=[["3月11日","1万ドル"],["6月10日","20万ドル"],["10月24日","70万ドル以上（約1.1億円）"]])),
 (2,"A",dict(img=29,year="2026年10月",head=["柱を失っても、","伸び続けた。"])),
 (4,"B",dict(kind="compare",title="光と影",sub="いい所と問題を、分けて見る",items=[["光","ゼロからAIでアプリを公開"],["光","途中の数字を公開し続けた"]],note="次は、影の部分")),
 (3,"A",dict(img=31,year="影 ①",head=["数字の多くは、","本人の投稿。"])),
 (4,"B",dict(kind="compare",title="記事どうしで、数字が合わない",sub="この動画では、本人の投稿の数字を使う",items=[["ある記事","毎月の定期収入 6万ドル"],["本人の投稿","直近28日の売上 6万ドル"]])),
 (4,"A",dict(img=33,year="影 ②",head=["集客の道は、","1本だった。"])),
 (3,"B",dict(kind="icons",title="学べること ①　作る前に、使いたい人を",sub="ポッドキャストから",items=["順番待ち 300人","作る前に集める","作るのはそのあと"])),
 (2,"A",dict(img=35,year="学べること ②",head=["使ったら、","数字で確かめる。"])),
 (3,"B",dict(kind="steps",title="この話から学べること",sub="3つにまとめると",items=["作る前に、使いたい人を見つける","お金を使ったら、数字で確かめる","集客の道を、1本にしない"],hi=2)),
 (2,"A",dict(img=37,year="",head=["差がつくのは、","届け方。"])),
 (2,"B",dict(kind="end",title="海外の1人の挑戦を、日付と数字で",sub="AI動画チャンネル",items=["チャンネル登録で、次の挑戦の記録へ"])),
]
assert sum(s[0] for s in S)==len(L["lines"]),sum(s[0] for s in S)
out=[];k=0
for n,t,d in S:
    ls=L["lines"][k:k+n]; tags=[x for tg in L["src"][k:k+n] for x in tg]
    ch=L["chap"][k]; k+=n
    d.update(type=t,lines=ls,source="・".join(dict.fromkeys(SRC[x] for x in tags)),chapter=(f"第{ch[0]}章｜{ch[1]}" if 0<ch[0]<11 else ("はじめに" if ch[0]==0 else "おわりに")))
    out.append(d)
json.dump(out,open("scenes.json","w"),ensure_ascii=False,indent=1)
print(len(out),"scenes")
