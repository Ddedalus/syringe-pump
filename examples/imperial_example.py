""" Play the Iperial March by changing motor speed. """
# Adapted from https://www.instructables.com/Music-With-Servo-Motor/
import asyncio

import aioserial

from syringe_pump import Pump

AS3 = 233
C4 = 262
D4 = 294
E4 = 330
F4 = 349
G4 = 392
GS4 = 415
A4 = 440
AS4 = 466
B4 = 494
C5 = 523
CS5 = 554
D5 = 587
DS5 = 622
E5 = 659
F5 = 699
FS5 = 740
G5 = 784
GS5 = 831
A5 = 880
PAUSE = 0

notes = [
    *[A4, PAUSE, A4, A4, A4, A4, PAUSE, A4, A4, A4, A4],
    *[PAUSE, A4, A4, A4, F4, F4, F4, C5, C5, C5],  # Intro 1 (21 Notes)
    *[A4, PAUSE, A4, A4, A4, A4, PAUSE, A4, A4, A4, A4],
    *[PAUSE, A4, A4, A4, F4, F4, F4, C5, C5, C5],  # Intro 2 (21 Notes)
    *[A4, A4, A4, F4, C5, A4, F4, C5, A4],  # Part 1  (9 Notes)
    *[PAUSE, E5, E5, E5, F5, C5, GS4, F4, C5, A4],  # Part 2  (10 Notes)
    *[PAUSE, A5, A4, A4, A5, GS5, G5, FS5, F5, FS5],  # Part 3  (10 Notes)
    *[PAUSE, AS4, DS5, D5, CS5, C5, B4, C5],  # Part 4  (8 Notes)
    *[PAUSE, F4, GS4, F4, A4, C5, A4, C5, E5],  # Part 5  (9 Notes)
    *[PAUSE, A5, A4, A4, A5, GS5, G5, FS5, F5, FS5],  # Part 6  (10 Notes)
    *[PAUSE, AS4, DS5, D5, CS5, C5, B4, C5],  # Part 7  (8 Notes)
    *[PAUSE, F4, GS4, F4, C5, A4, F4, C5, A4],  # Part 8  (9 Notes)
]

beats = [
    *[1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Intro 1
    *[1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Intro 2
    *[4, 4, 4, 3, 1, 4, 3, 1, 4],  # Part 1
    *[4, 4, 4, 4, 3, 1, 4, 3, 1, 4],  # Part 2
    *[4, 4, 3, 1, 4, 3, 1, 1, 1, 1],  # Part 3
    *[3, 2, 4, 3, 1, 1, 1, 1],  # Part 4
    *[3, 2, 4, 3, 1, 4, 3, 1, 4],  # Part 5
    *[3, 4, 3, 1, 4, 3, 1, 1, 1, 1],  # Part 6
    *[3, 2, 4, 3, 1, 1, 1, 1],  # Part 7
    *[3, 2, 4, 3, 1, 4, 3, 1, 4],  # Part 8
]

tempo = 180 / 1000  # ms
max_rate = 5  # max flow of the syringe pump, in ml/min
start_at = 43  # skip the intros which don't work well


async def tune(pump: Pump):
    await pump.set_brightness(0)  # disable screen to avoid flicker
    for note, beat in zip(notes[start_at:], beats[start_at:]):
        if rate := max_rate * note / A5:
            await pump.infusion_rate.set(rate)
            await pump.run()
        else:  # pause between notes
            await pump.stop()

        duration = float(beat) * tempo  # length of note/rest in ms
        await asyncio.sleep(duration)  # wait for tone to finish

        await pump.stop()  # brief pause between notes
        await asyncio.sleep(tempo / 10.0)


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
