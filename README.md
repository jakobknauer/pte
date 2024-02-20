# PTE - Python Text Editor

PTE is a modal text editor written in Python, inspired by Vim.

PTE uses [curses](https://docs.python.org/3/library/curses.html) for the text user interface,
and [Pygments](https://pygments.org/) for syntax highlighting.


## Install & Run

__Note:__ The following instructions assume you're using Arch Linux. In other environments, slight changes (such as exchanging `python` by `python3`) might be necessary.


### As a Python package

Use `pip install .` to install the program and its dependencies into the currently active (virtual) environment.
Then run the program using `python -m pte.run <args>` from anywhere in your virtual environment,
or `./scripts/run.sh <args>` if you're in the repository root directory.


### As an executable

Use `./scripts/install.sh` to install the program executable to `~/.local/bin/pte`. Dependencies are installed into a virtual environment located in `~/.local/lib/pte`.
If the directory `~/.local/bin` is in your `$PATH`, you may then run the program using the command `pte <args>`.


## Usage

### Command-line options

The following also applies if instead of using `pte`, you run the program via `python -m pte.run` or `./scripts/run.sh`.

```bash
# Run PTE without loading or creating a document
pte

# Run PTE and load a file
pte example.txt

# Print version info and exit
pte --version
```


### Modes

PTE uses modes similar to vim. The three modes currently existing are:
- __Normal Mode__, mainly for navigating a document.
- __Insert Mode__, for inserting text.
- __Command Mode__, for running more intricate commands.

The current mode is displayed at the beginning of the status bar (the second-to-last line on screen).


#### Normal Mode

After starting PTE or loading or creating a document, you are in Normal Mode.

Basic navigation:
- Use h/j/k/l to navigate left/down/up/right.
- Jump to the start (resp. end) of the current line using H (resp. L).
- Jump to the last (resp. first) line of the document using J (resp. K).
 
Enter Insert Mode:
- Use i (resp. a) to enter insert mode at (resp. after) the current cursor position.
- Use I (resp. A) to enter insert mode before the first (resp. after the last) character of the current line.
- Use o (resp. O) to enter insert mode in a new blank line below (resp. above) the current line.

Enter Command Mode:
- Use : to enter command mode with an empty command.
- Use / to enter command mode with the command `search ` already spelled out.
- Use CTRL-R to enter command mode with the command `replace ` already spelled out.

Deletion:
- Use x (resp. X) to delete the character under (resp. before) the current cursor position.
- Use dd to delete the current line.

Quit:
- Use ZQ to quit without saving.
- Use ZZ to quit with saving the document to the location from where it was loaded.


#### Insert Mode

- Type a printable character (such as letters, digits, spaces, or special characters) to insert the character at the current cursor position and move the cursor one position to the right.
- Use Enter to insert a new line.
- Use Tab to insert 4 spaces.
- Use Backspace to delete the character before the cursor or, if the cursor is on the first character of the line, to join the line with the one above it.
- Use Escape to leave Insert Mode and enter Normal Mode.


#### Command Mode

- Type a printable character to enter a command in the command line (the last line on screen), use Backspace to delete the last character.
- Use Enter to execute the command and switch to Normal Mode.
- Use Escape to discard the current command and switch to Normal Mode.

The following commands are available:
- `load <filepath>`: Load a document from the specified file.
- `save`: Save the document to the file from where it was loaded, or to which it was last saved. If neither of those two apply, the document is not saved.
- `save <filepath>`: Save the document to the specified file.
- `quit`: Quit PTE without saving.
- `empty`: Create an empty document.
- `search <pattern>`: Jump to the next occurence of the specified pattern. All occurences of the pattern are highlighted while in command mode.
- `replace <pattern> <substitute>`: Replace all occurences of the specified pattern in the document by the specified substitute. All occurences of the pattern are highlighted while in command mode.
- `syntax`: Enable syntax highlighting for the current document, detect filetype automatically. This is implemented using [pygments.lexers.guess_lexer](https://pygments.org/docs/api/#pygments.lexers.guess_lexer).
- `syntax <syntax name>`: Enable syntax highlighting for the current document, using the specified syntax. This is implemented using [pygments.lexers.get_lexer_by_name](https://pygments.org/docs/api/#pygments.lexers.get_lexer_by_name).
- `nosyntax`: Disable syntax highlighting for the document.

You may use CTRL+R to switch from `search <pattern>` to `replace <pattern>`.
