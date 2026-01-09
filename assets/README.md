# MIDI Drum Remapper

This is a conversion software used to import drum MIDI files created in a DAW into score writing software like MuseScore **without issues**.

MIDI files exported from a DAW generally do not follow drum specifications as is, and importing them into score writing software often does not go well.  
By converting MIDI files with this software, they become MIDI files that follow drum specifications and can be imported without problems.

Internally, it only performs MIDI number remapping, so it can be used not only for scores but also for conversion between drum sound sources by writing a map definition file.

## About Map Definition Files

Map definition files are placed as `.xml` files in the `mappings` directory.
Several presets corresponding to major drum sound sources are already provided, but you can also create your own if they are insufficient.
Detailed specifications are explained below.

### Main Elements and Attributes

#### 1. `<Note>` Element
Defines basic note conversion rules.

*   **from**: (Required) Source MIDI note number (0-127)
*   **to**: (Required) Destination MIDI note number (0-127)
*   **velocity**: (Optional) Specify this if you want to fix the output velocity to a constant value (0-127). If not specified, the original velocity is maintained.

Example:
```xml
<!-- Convert note 36 to note 20 -->
<Note from="36" to="20"/>

<!-- Convert note 38 to note 40 and fix velocity to 127 -->
<Note from="38" to="40" velocity="127"/>
```

#### 2. `<Group>` Element
An element to group notes that share a common destination MIDI note number.

*   **to**: (Required) Destination MIDI note number (0-127)
*   **velocity**: (Optional) Output velocity (common within the group) (0-127)
*   Define `<Note>` as child elements of this element.

`<Note>` elements inside `<Group to="XX">` do not need to specify the `to` attribute.
If `velocity` is specified in both `Group` and `Note`, **the `Note` side takes precedence**.

Example:
```xml
<!-- Convert notes 36 and 40 to note 38. Note 36 has velocity 100, Note 40 has velocity 127 (from Group) -->
<Group to="38" velocity="127">
    <Note from="36" velocity="100"/>
    <Note from="40"/>
</Group>
```

## MuseScore Drum MIDI Note Numbers

Please use this as a reference when you want to convert to MuseScore.

For a general 3-tom setup, recommended values are High Tom = 48, Low Tom = 47, Floor Tom = 43.

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

27: High Q  
28: Slap  
29: Scratch Push  
30: Scratch Pull  
31: Sticks  
32: Square Click  
33: Metronome Click  
34: Metronome Bell  
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
