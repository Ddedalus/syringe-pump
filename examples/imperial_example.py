import asyncio
import time

import aioserial

from syringe_pump import Pump

NOTE_AS3 = 233
NOTE_C4 = 262
NOTE_D4 = 294
NOTE_E4 = 330
NOTE_F4 = 349
NOTE_G4 = 392
NOTE_GS4 = 415
NOTE_A4 = 440
NOTE_AS4 = 466
NOTE_B4 = 494
NOTE_C5 = 523
NOTE_CS5 = 554
NOTE_D5 = 587
NOTE_DS5 = 622
NOTE_E5 = 659
NOTE_F5 = 699
NOTE_FS5 = 740
NOTE_G5 = 784
NOTE_GS5 = 831
NOTE_A5 = 880

rhythmBuzzerPin = 9
rhythmLength = 115

rhythmNotes = [
    NOTE_A4,
    0,
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    0,
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    0,
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    NOTE_F4,
    NOTE_F4,
    NOTE_F4,
    NOTE_C5,
    NOTE_C5,
    NOTE_C5,  # Intro 1 (21 Notes)
    NOTE_A4,
    0,
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    0,
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    0,
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    NOTE_F4,
    NOTE_F4,
    NOTE_F4,
    NOTE_C5,
    NOTE_C5,
    NOTE_C5,  # Intro 2 (21 Notes)
    NOTE_A4,
    NOTE_A4,
    NOTE_A4,
    NOTE_F4,
    NOTE_C5,
    NOTE_A4,
    NOTE_F4,
    NOTE_C5,
    NOTE_A4,  # Part 1  (9 Notes)
    0,
    NOTE_E5,
    NOTE_E5,
    NOTE_E5,
    NOTE_F5,
    NOTE_C5,
    NOTE_GS4,
    NOTE_F4,
    NOTE_C5,
    NOTE_A4,  # Part 2  (10 Notes)
    0,
    NOTE_A5,
    NOTE_A4,
    NOTE_A4,
    NOTE_A5,
    NOTE_GS5,
    NOTE_G5,
    NOTE_FS5,
    NOTE_F5,
    NOTE_FS5,  # Part 3  (10 Notes)
    0,
    NOTE_AS4,
    NOTE_DS5,
    NOTE_D5,
    NOTE_CS5,
    NOTE_C5,
    NOTE_B4,
    NOTE_C5,  # Part 4  (8 Notes)
    0,
    NOTE_F4,
    NOTE_GS4,
    NOTE_F4,
    NOTE_A4,
    NOTE_C5,
    NOTE_A4,
    NOTE_C5,
    NOTE_E5,  # Part 5  (9 Notes)
    0,
    NOTE_A5,
    NOTE_A4,
    NOTE_A4,
    NOTE_A5,
    NOTE_GS5,
    NOTE_G5,
    NOTE_FS5,
    NOTE_F5,
    NOTE_FS5,  # Part 6  (10 Notes)
    0,
    NOTE_AS4,
    NOTE_DS5,
    NOTE_D5,
    NOTE_CS5,
    NOTE_C5,
    NOTE_B4,
    NOTE_C5,  # Part 7  (8 Notes)
    0,
    NOTE_F4,
    NOTE_GS4,
    NOTE_F4,
    NOTE_C5,
    NOTE_A4,
    NOTE_F4,
    NOTE_C5,
    NOTE_A4,
]  # Part 8  (9 Notes)

rhythmBeats = [
    1,
    2,
    1,
    1,
    1,
    1,
    2,
    1,
    1,
    1,
    1,
    2,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,  # Intro 1
    1,
    2,
    1,
    1,
    1,
    1,
    2,
    1,
    1,
    1,
    1,
    2,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,  # Intro 2
    4,
    4,
    4,
    3,
    1,
    4,
    3,
    1,
    4,  # Part 1
    4,
    4,
    4,
    4,
    3,
    1,
    4,
    3,
    1,
    4,  # Part 2
    4,
    4,
    3,
    1,
    4,
    3,
    1,
    1,
    1,
    1,  # Part 3
    3,
    2,
    4,
    3,
    1,
    1,
    1,
    1,  # Part 4
    3,
    2,
    4,
    3,
    1,
    4,
    3,
    1,
    4,  # Part 5
    3,
    4,
    3,
    1,
    4,
    3,
    1,
    1,
    1,
    1,  # Part 6
    3,
    2,
    4,
    3,
    1,
    1,
    1,
    1,  # Part 7
    3,
    2,
    4,
    3,
    1,
    4,
    3,
    1,
    4,
]  # Part 8

tempo = 180
max_rate = 5


async def tune(pump: Pump):
    await pump.set_brightness(0)
    while True:
        for i in range(rhythmLength):  # step through the song arrays
            if i < 43:
                continue
            rhythmDuration = rhythmBeats[i] * tempo  # length of note/rest in ms
            if rhythmNotes[i] == "0":  # is this a rest?
                await pump.stop()
                await asyncio.sleep(rhythmDuration / 1000)  # then pause for a moment
            else:  # otherwise, play the note
                rate = max_rate * rhythmNotes[i] / NOTE_A5
                if rate == 0:
                    await pump.stop()
                    continue
                await pump.start()
                await pump.set_infusion_rate(rate)
                await asyncio.sleep(rhythmDuration / 1000)  # wait for tone to finish
            await pump.stop()
            await asyncio.sleep(tempo / 10000)  # brief pause between notes


async def main(pump: Pump):
    try:
        await tune(pump)
    except (Exception, KeyboardInterrupt):
        print("Emergency stop...")
    finally:
        await pump.stop()
        await pump.set_brightness(15)


if __name__ == "__main__":
    serial = aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)
    pump = Pump(serial=serial)
    asyncio.run(main(pump))
