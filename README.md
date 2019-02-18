-World Clock for your Python-

This allows you to know time difference all over the world.

# Usage
Simply use slice as clock!

```
>>>from worldclock import tokyo, seoul, london, paris, new_delhi
```


# show time
Don't hesitate to put numbers directly!

```
>>>tokyo[23:15]
[23:15]
```

## convert to other place's time

```
>>> london(tokyo[23:15])
[14:15]
```


## compare 2 times, earlier, same or later

```
>>> tokyo[20:00] == seoul[20:00]
True
>>> # which is earlier or later
>>> paris[6:30] > new_delhi[10:40]
True
```

# about
- fetchtimezone.py
used to generate worldclock.py by Powershell `tzutil` command

- sliceclock.py
define classes for the clocks

- worldclock.py
use this if you want to show clocks

# tricks
This script uses some tricks to use slice as clock (, like `tokyo[12:00]`).

Also, it uses `datetime` for time calculations.