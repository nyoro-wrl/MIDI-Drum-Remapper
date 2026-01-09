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

一般的な3タム配置のおすすめは、ハイタム=48、ロータム=47、フロアタム=43です。

36: Bass Drum 1
35: Bass Drum 2
38: Acoustic Snare
40: Electric Snare
37: Side Stick
42: Closed Hi-Hat
46: Open Hi-Hat
44: Pedal Hi-Hat
50: High Tom
48: Hi-Mid Tom
47: Low-Mid Tom
45: Low Tom
43: High Floor Tom
41: Low Floor Tom
51: Ride Cymbal 1
53: Ride Bell
59: Ride Cymbal 2
49: Crash Cymbal 1
57: Crash Cymbal 2
55: Splash Cymbal
52: China Cymbal

31: Sticks
39: Hand Clap
54: Tambourine
56: Cowbell
58: Vibraslap
60: Hi Bongo
61: Low Bongo
62: Mute Hi Conga
63: Open Hi Conga
64: Low Conga
65: High Timbale
66: Low Timbale
67: High Agogo
68: Low Agogo
69: Cabasa
70: Maracas
71: Short Whistle
72: Long Whistle
73: Short Guiro
74: Long Guiro
75: Claves
76: High Wood Block
77: Low Wood Block
78: Mute Cuica
79: Open Cuica
80: Mute Triangle
81: Open Triangle
82: Shaker
83: Sleigh Bell
84: Mark Tree
85: Castanets
86: Mute Surdo
87: Open Surdo

27: High Q
28: Slap
29: Scratch Push
30: Scratch Pull
32: Square Click
33: Metronome Click
34: Metronome Bell