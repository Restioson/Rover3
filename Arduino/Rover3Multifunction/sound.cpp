#include <Arduino.h>
#include "sound.h"

#define SPEAKER_PIN 7

void note(unsigned int frequency, unsigned long duration) {
  tone(SPEAKER_PIN, frequency, duration);
}

int melody[] = {
  NOTE_C4, NOTE_G3, NOTE_G3, NOTE_A3, NOTE_G3, 0, NOTE_B3, NOTE_C4
};

// note durations: 4 = crochet, 8 = quaver, etc.:
int note_durations[] = {
  4, 8, 8, 4, 4, 4, 4, 4
};

void playMelody() {
  for (int i = 0; i < 8; i++) {
    // to calculate the note duration, take one second
    // divided by the note type.
    //e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    int note_duration = 1000 / note_durations[i];
    note(melody[i], note_duration);

    int pause = note_duration * 1.30;
    delay(pause);
    noTone(SPEAKER_PIN);
  }
}
