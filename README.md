# Gravity simulation

## Installation
1) Download and install python
2) Install *pygame*

	`$ pip install --user pygame` (user only)
	
	or

	`$ pip install pygame` (all users, requires root privileges)

## Run
- Run `main.py` 
- Optionally use the `run.bat` batch file to run the program
- `CMD.bat` can be used to access the command line

## Controls
- **Ctrl + Space**: Pause and Resume
- **Mouse wheel**: Zoom in and out according to cursor position
- **Mouse click on body**: Fix the view to that body
- **Ctrl + Plus**: Speed up time
- **Ctrl + Minus**: Slow down time
- **Ctrl + d**: Replace sun with 2 suns
- **Ctrl + m**: Fix view to earth' moon

## Fact check
| Value         		| Reality		| Simulation	|
| ---------------------	|:-------------:| -------------:|
| Earth max velocity	| 30 290 m/s	| 30 275 m/s	|
| Mercury max velocity	| 58 980 m/s	| 58 999 m/s	|


### Data source
Planet *fact sheets* from https://nssdc.gsfc.nasa.gov/planetary/
*Aphelion*: Initial distance from sun (x position)
*Min. orbital velocity*: initial velocity (y velocity)

#### Darius & Bennet
