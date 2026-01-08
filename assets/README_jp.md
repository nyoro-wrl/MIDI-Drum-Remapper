# MIDI Drum Remapper

DAWで打ち込んだドラムMIDIファイルを、MuseScoreなどの楽譜ソフトに **問題なく** インポートするために使う変換ソフトです。
DAWから出力したMIDIファイルは、そのままではドラムの仕様に沿っておらず、楽譜ソフトにインポートするとうまくいきません。
そこでこのソフトでMIDIファイルの変換を行うことで、ドラムの仕様に沿ったMIDIファイルになり、問題なくインポートすることができます。

内部的にはMIDI番号のリマップを行っているだけなので、楽譜用としてだけでなく、ドラム音源間の変換もマップ定義ファイルを書けば可能です。

## マップ定義ファイルについて

マップ定義ファイルは`mappings`ディレクトリに`.xml`ファイルとして配置します。
主要なドラム音源に対応したいくつかのプリセットを用意済みですが、足りなければ自分で作成することも可能です。
以下に詳細な仕様を説明します。

### 主な要素と属性

#### 1. `<Note>` 要素
基本的なノート変換ルールを定義します。

*   **from**: (必須) 変換元のMIDIノート番号 (0-127)
*   **to**: (必須) 変換先のMIDIノート番号 (0-127)
*   **velocity**: (任意) 出力ベロシティを固定値にする場合に指定します (0-127)。指定しない場合は、元のベロシティが維持されます。

例:
```xml
<!-- ノート36をノート20に変換 -->
<Note from="36" to="20"/>

<!-- ノート38をノート40に変換し、ベロシティを127に固定 -->
<Note from="38" to="40" velocity="127"/>
```

#### 2. `<If>` 要素 (条件付きマッピング)
特定の入力ベロシティに対して、特別なマッピングルールを適用する場合に使用します。

*   **velocity**: (必須) 条件となる入力ベロシティ (0-127)
*   この要素の子要素として `<Note>` を定義します。

例:
```xml
<!-- 入力ベロシティが127の場合のみ適用されるルール -->
<If velocity="127">
    <!-- ベロシティ127でノート38が来た場合、ノート40に変換 -->
    <Note from="38" to="40"/>
</If>
```

## MuseScore ドラムMIDIノート番号

MuseScoreに変換したい場合の参考にしてください。

36: Kick 1
35: Kick 2
38: Snare
37: Sidestick
42: Closed Hi-Hat
46: Open Hi-Hat
44: Pedal Hi-Hat
50: High Tom
48: High Mid Tom (Generally: High Tom)
47: Low Mid Tom (Generally: Low Tom)
45: Low Tom
43: High Floor Tom (Generally: Floor Tom)
41: Low Floor Tom
51: Ride Cymbal 1
53: Ride Bell
59: Ride Cymbal 2
49: Crash Cymbal Left
57: Crash Cymbal Right
55: Splash Cymbal
60: China Cymbal
54: Tambourine
56: Cowbell
40: Electric Snare
