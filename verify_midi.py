from mido import MidiFile
import sys

def parse_notes(filename):
    notes = []
    try:
        mid = MidiFile(filename)
        for i, track in enumerate(mid.tracks):
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    notes.append((msg.note, msg.channel))
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
    return notes

def verify():
    input_file = "input.mid"
    output_file = "output.mid"
    
    print(f"Analyzing {input_file}...")
    input_data = parse_notes(input_file) # List of (note, channel)
    input_notes = [n[0] for n in input_data]
    input_channels = set([n[1] for n in input_data])
    
    print(f"Found {len(input_notes)} note events.")
    print(f"Unique input notes: {sorted(list(set(input_notes)))}")
    print(f"Input channels: {input_channels}")

    print(f"\nAnalyzing {output_file}...")
    output_data = parse_notes(output_file)
    output_notes = [n[0] for n in output_data]
    output_channels = set([n[1] for n in output_data])
    
    print(f"Found {len(output_notes)} note events.")
    print(f"Unique output notes: {sorted(list(set(output_notes)))}")
    print(f"Output channels: {output_channels}")
    
    # Check if all output is on channel 9 (Channel 10)
    if output_channels == {9}:
        print("\n[OK] All output notes are on Channel 10 (index 9).")
    else:
        print(f"\n[WARNING] Output notes are on channels: {output_channels}. Expected only {9}.")

    # Show first few comparisons
    print("\nFirst 10 note mappings (Input -> Output):")
    for i in range(min(10, len(input_notes), len(output_notes))):
        print(f"  {input_notes[i]} -> {output_notes[i]}")

if __name__ == "__main__":
    verify()
