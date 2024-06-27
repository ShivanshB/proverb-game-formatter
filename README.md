# proverb-game-formatter
Generator for the formatting of a proverb based word game. Available for use in newspapers and magazines.

## General Formatting
1. Try to use only one space between words. If not, the program will collapse spaces, though it may lead to odd formatting.
2. When filling out the bottom field on the user interface--"Enter Indices of Letters to Reveal"--the letters are indexed starting at one. For example, if the proverb is "to be or not to be", and we want the "n" and "t" in "not" to be revealed, we would enter "10, 12" into this field.
3. The "clue" should not exceed one line (about 65 characters) in length.
4. The message for "yesterday's P.A.S.S.WORDS" should not exceed two lines (about 120 characters) in length.
5. No single word in the proverb should exceed 21 characters in length.
6. Only letters and spaces will be displayed in boxes. All special characters (colons, semicolons, etc) or numbers (1, 2, etc) will be removed before displaying.
7. When entering the "PDF Filename" into the user interface, make sure that it is in the form "NAME.pdf". If it does not follow this format, the form will tell you and allow you to change the name.

## Notes
1. All generated puzzles are automatically put into "Documents/puzzles". Note that if this folder already exists, **it will be overridden**
2. The log file containing date & time, proverb, clue, the previous day's answer, and the revealed letter indices is found at "Documents/puzzles/logs"
3. **Important**: If the name entered into "Enter PDF Filename" is the same as the name of an old puzzle already in "Documents/puzzles", it will override the old puzzle pdf. **Make sure that your puzzles have unique names if you do not want this behaviour.**

# How to Run (MacOS)
1. Download the .zip file found [here](https://drive.google.com/drive/folders/1lujT_gsKyhypGxpFp44XeJSjKEC-XHuL?usp=sharing).
2. Double click the .zip file once downloaded to unpack application.
4. Drag the Application Icon for the "PuzzleGenerator" app into your Applications folder. It may be helpful to also drag it into your Dock and right click --> options --> keep in dock. This will allow for later ease of use.
5. To boot the application, find the Application logo in Finder. Right click the application logo and click open. If a small user interface opens, you are good. If not, click the application again from your dock.
7. **Note**: Before running, make sure to read the above sections on 'General Formatting' and 'Notes'. Importantly, note that all puzzles will be saved in 'Documents/puzzles'. **If this folder exists, it will be overriden.**
8. Enter the required info and click submit at the bottom. A small popup will come up. If it displays an error, click "OK" and fix the fields before clicking submit again. If it does not display any errors, click "OK" and your puzzle should be located at "Documents/puzzles" and popup on the screen. A log of all created puzzles should be stored at 'Documents/puzzles/logs'.
