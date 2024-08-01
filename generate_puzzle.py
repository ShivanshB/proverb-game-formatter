import os
import sys
import re
import csv
import random
import datetime
import reportlab
import subprocess
import tkinter as tk

from tkinter import messagebox
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

# Global Vars for GUI
PDF_PATTERN = r'^.+\.pdf$'
DATA_SUBMITTED = False
user_input_data = {
    "filename": "",
    "proverb": "",
    "clue": "",
    "prev": "",
    "integers": []
}

# params
# --------------------------------------
WIDTH = 612.0 # default pagesize letter
HEIGHT = 792.0 # default pagesize letter
MARGIN = 36.0
PADDING = 15.0

PUZZLE_TOP_Y = 550 # distance from bottom of page that boxes/rect start --> should depend on other vars?
LINE_SPACING = 25
FOOTER_SPACING = LINE_SPACING # distance from bottom of last box to top of clue, vertically
TITLE_SPACING = 40.0

BOX_LEN = 25 # space between boxes = BOX_LEN
TRIANGLE_HEIGHT = 25

TITLE_LARGE_FONT_SIZE = 30
LOGO_LARGE_FONT_SIZE = 20
LOGO_NORMAL_FONT_SIZE = 17
TITLE_NORMAL_FONT_SIZE = 25
AUTHOR_FONT_SIZE = 15
DESCRIPTION_FONT_SIZE = 13
LETTER_FONT_SIZE = 18
BODY_FONT_SIZE = 12
BODY_FONT = "Helvetica"
BODY_FONT_BOLD = "Helvetica-Bold"
BODY_FONT_OBLIQUE = "Helvetica-Oblique"
BODY_FONT_BOLD_OBLIQUE = "Helvetica-BoldOblique"
FOOTER_FONT_SIZE = 13

CIRCLE_RADIUS = 22
CIRCLE_SPACE = 5 # horizontal space between circles
CIRCLE_Y = PUZZLE_TOP_Y + TRIANGLE_HEIGHT + BOX_LEN + CIRCLE_RADIUS + 20# 20 is tunable
DESCRIPTION_TOP_Y = CIRCLE_Y + CIRCLE_RADIUS + LINE_SPACING/2 + BODY_FONT_SIZE + LINE_SPACING * (1/4) # both denoms tunable

LOG_FILENAME = "log.csv"
FOLDER = "puzzles/"

PATTERN = '[^A-Za-z ]'

CHAR_TO_NUM = {'A': 1, 'B': 1, 'C': 1, 
               'D': 2, 'E': 2, 'F': 2,
               'G': 3, 'H': 3, 'I': 3,
               'J': 4, 'K': 4, 'L': 4,
               'M': 5, 'N': 5, 'O': 5,
               'P': 6, 'Q': 6, 'R': 6,
               'S': 7, 'T': 7, 'U': 7,
               'V': 8, 'W': 8,
               'X': 9, 'Y': 9, 'Z': 9}

CIRCLES = ['ABC','DEF','GHI','JKL','MNO','PQR','STU','VW','XYZ']

# useful definitions
#------------------------------------
x_l, x_h = MARGIN, WIDTH - MARGIN
y_l, y_h = MARGIN, HEIGHT - MARGIN
x_center, y_center = (x_l + x_h)/2, (y_l + y_h)/2
ch_per_line = int((WIDTH - (2 * MARGIN)) // BOX_LEN)
box_vertical_spacing = TRIANGLE_HEIGHT + BOX_LEN + LINE_SPACING
#------------------------------------

def separate_lines(proverb, n):
    line_intervals = [] # intervals of the form (start, end) for each generated line
    cur_line_interval = [0, None] 
    cur_len = 0 # length of the current line
    prev_word_start = 0 # idx of the last word's first character
    
    for i in range(n):
        # checking if this is the last character in the line
        if cur_len == ch_per_line - 1:
            # if last char in the line is a space
            if proverb[i] == ' ':
                cur_line_interval[1] = i
                line_intervals.append(cur_line_interval)
                cur_line_interval = [i + 1, None]
                prev_word_start = i + 1
                cur_len = 0
            else:
                # if last char in the line is the end of the whole proverb
                if i == (n - 1):
                    cur_line_interval[1] = i + 1
                    line_intervals.append(cur_line_interval)
                # if the last char in the line is the end of a word (and not end of proverb)
                elif proverb[i + 1] == ' ':
                    cur_line_interval[1] = i + 1
                    line_intervals.append(cur_line_interval)
                    cur_line_interval = [i + 2, None]
                    cur_len = 0
                # if we are currently breaking up a word
                else:
                    cur_line_interval[1] = prev_word_start - 1
                    line_intervals.append(cur_line_interval)
                    cur_line_interval = [prev_word_start, None]
                    cur_len = i - prev_word_start + 1
        # end of proverb
        elif i == (n-1):
            cur_line_interval[1] = n
            line_intervals.append(cur_line_interval)
        # continue through letters
        else:
            if proverb[i] == ' ':
                prev_word_start = i + 1
            cur_len += 1
            
    return line_intervals

def draw_boxes_triangles(c, lines, line_offsets, letter_reveals):
    for line_num, line in enumerate(lines):
        for i, ch in enumerate(line):
            if ch != ' ':
                # bottom right x-coord of box
                box_x = x_center + ((i - len(line)/2)* BOX_LEN)
                # bottom right y-coord of box
                box_y= PUZZLE_TOP_Y - (line_num * box_vertical_spacing)
                # drawing box for letter
                c.rect(box_x, box_y, BOX_LEN, BOX_LEN, stroke=1, fill=0)
                
                # setting font to letter
                c.setFont(BODY_FONT, LETTER_FONT_SIZE)
                
                # drawing in letter if needs to be revealed
                ch_num = line_offsets[line_num] + i # idx of char in original proverb
                if (ch_num + 1) in letter_reveals:
                    ch_width = stringWidth(ch, BODY_FONT, LETTER_FONT_SIZE)
                    ch_x = box_x + (BOX_LEN/2) - (ch_width/2)
                    ch_y = box_y + (BOX_LEN - LETTER_FONT_SIZE) * 1.00 # 1.00 is tunable
                
                    # drawing letter in box
                    c.drawString(ch_x, ch_y, ch)  
                
                # setting font back to body
                c.setFont(BODY_FONT_BOLD, BODY_FONT_SIZE)

                 # bottom vertex
                bottom_vx_x, bottom_vx_y = box_x + (BOX_LEN/2), box_y + BOX_LEN
                # top left vertex
                top_l_vx_x, top_l_vx_y = box_x, box_y + (BOX_LEN + TRIANGLE_HEIGHT)
                # top right vertex
                top_r_vx_x, top_r_vx_y = box_x + BOX_LEN, box_y + (BOX_LEN + TRIANGLE_HEIGHT)

                # draw lines connecting vertices
                c.line(bottom_vx_x, bottom_vx_y, top_l_vx_x, top_l_vx_y)
                c.line(bottom_vx_x, bottom_vx_y, top_r_vx_x, top_r_vx_y)
                c.line(top_l_vx_x, top_l_vx_y, top_r_vx_x, top_r_vx_y)

                # finding center of triangle
                tr_middle_x, tr_middle_y = bottom_vx_x, (top_l_vx_y + bottom_vx_y)/2

                # finding width of text for centering
                num = str(CHAR_TO_NUM[ch])
                text_width = stringWidth(num, BODY_FONT_BOLD, BODY_FONT_SIZE)

                # finding bottom left of text
                text_x = tr_middle_x - (text_width/2)
                text_y = tr_middle_y - (BODY_FONT_SIZE/6) # approximate, might need some fiddling

                # drawing in letter
                c.drawString(text_x, text_y, num)

def draw_circles(c):
    # compute number of circles
    num_circles = len(CIRCLES)
    
    for i, text in enumerate(CIRCLES):
        # offset to center circles horizontally
        offset = 0.5 * ((CIRCLE_RADIUS * 2) * (num_circles - 1) + (num_circles - 1) * CIRCLE_SPACE)

        # circle center coords
        circle_x = (WIDTH/2) + (i * (2 * CIRCLE_RADIUS + CIRCLE_SPACE)) - offset
        circle_y = CIRCLE_Y - 10 # adjustable moving circles between description and boxes
 
        # draw circle
        c.circle(circle_x, circle_y, CIRCLE_RADIUS, stroke=1, fill=0)

        # finding width of text for centering
        text_width = stringWidth(text, BODY_FONT_BOLD, BODY_FONT_SIZE)
        text_x = circle_x - text_width/2
        text_y = circle_y + BODY_FONT_SIZE * 0.20 # 0.40 is tunable

        # writing text
        num = str(i+1)
        c.drawString(text_x, text_y, text)

        # finding width of number for centering
        num_width = stringWidth(num, BODY_FONT_BOLD, BODY_FONT_SIZE)
        num_x = circle_x - num_width/2
        num_y = circle_y - BODY_FONT_SIZE

        # writing number
        c.drawString(num_x, num_y, num)

def log_proverb(proverb, filename, clue, hidden_letters, filepath):
    # logging the proverb and it's date and time in a csv file
    file_exists = os.path.isfile(filepath)
    with open(filepath, 'a', newline='') as file:
        writer = csv.writer(file)
        # write header if the file doesn't exist
        if not file_exists:
            writer.writerow(['Date and Time', 'Proverb', 'Filename', 'Clue', 'Hidden Letters'])
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Year-Month-Day Hour:Minute:Second
        writer.writerow([date_time, proverb, filename, clue, hidden_letters])

def setup_file_structure():
    # Get the path to the user's home directory
    home_directory = os.path.expanduser('~')
    # Construct the path to the Documents directory
    documents_directory = os.path.join(home_directory, 'Documents')
    # Define the path to the puzzles folder within the Documents directory
    puzzles_directory = os.path.join(documents_directory, 'puzzles')
    
    # Print the path where the puzzles directory will be created or verified
    print(f"Creating or using existing folder at: {puzzles_directory}")
    
    # Check if the puzzles directory exists, and create it if it does not
    if not os.path.exists(puzzles_directory):
        os.makedirs(puzzles_directory)
        print("Folder created successfully.")
    else:
        print("Folder already exists.")
    
    return puzzles_directory

def clean_proverb(proverb):
    # removing all special character
    proverb = re.sub(PATTERN, '', proverb)
    
    # cleaning up spaces and making all uppercase
    proverb = list(proverb.upper().strip())
    
    # length of cleaned proverb
    n = len(proverb)
    
    return proverb, n

def randomize():
    # randomly shuffle circles
    random.shuffle(CIRCLES)

    # redo character to number mapping
    for idx, letters in enumerate(CIRCLES):
        for letter in letters:
            CHAR_TO_NUM[letter] = idx + 1


def draw_footer(c, clue, prev, num_lines):
    # properly format clue  
    clue_label = "Clue: "
    clue = clue.strip()
    is_clue = len(clue)
    
    # checking if there is a clue
    if is_clue:

        # setting font to bold for "Clue: "
        c.setFont(BODY_FONT_BOLD, FOOTER_FONT_SIZE)

        # calculating "Clue: " location
        clue_label_width = stringWidth(clue_label, BODY_FONT_BOLD, FOOTER_FONT_SIZE)
        clue_label_x = MARGIN + 0.50 * (WIDTH - (2 * MARGIN) - (ch_per_line * BOX_LEN))
        clue_label_y = PUZZLE_TOP_Y - ((num_lines - 1) * (TRIANGLE_HEIGHT + BOX_LEN) 
                                 + ((num_lines - 1) * LINE_SPACING)
                                 + FOOTER_FONT_SIZE
                                 + LINE_SPACING/2)

        # drawing in clue label
        c.drawString(clue_label_x, clue_label_y, clue_label)

        # setting font for Clue
        c.setFont(BODY_FONT_BOLD_OBLIQUE, FOOTER_FONT_SIZE)

        # calculating clue text location
        clue_x = clue_label_x + clue_label_width # 0.8 is tunable
        clue_y = clue_label_y

        # drawing in clue text
        c.drawString(clue_x, clue_y, clue)
    
    prev = prev.strip().upper()
    is_prev = len(prev)
    
    if is_prev:
        # writing yesterday's answer
        pt1, pt2, pt3 = "Yesterday's ", "P.A.S.S.", "WORDS: " # normal, bold, normal
        pt1_width = stringWidth(pt1, BODY_FONT, FOOTER_FONT_SIZE)
        pt2_width = stringWidth(pt2, BODY_FONT_BOLD, FOOTER_FONT_SIZE)
        pt3_width = stringWidth(pt3, BODY_FONT, FOOTER_FONT_SIZE)
        prev_width = stringWidth(prev, BODY_FONT_OBLIQUE, FOOTER_FONT_SIZE)
        
        # calculating widths for all text
        label_width = pt1_width + pt2_width + pt3_width
        total_width = label_width + prev_width
        max_width = WIDTH - MARGIN * 2
        
        # maximum of two lines for this section (previous day's proverb)
        split_point = None
        if total_width > max_width:
            word_breaks = [i for i, ch in enumerate(prev) if ch == ' ']
            
            # iterating backward through word breaks to see where to split new line
            for break_idx in word_breaks[::-1]:
                new_width = stringWidth(prev[:break_idx], BODY_FONT_OBLIQUE, FOOTER_FONT_SIZE)
                # width of second line, with leading space removed
                remaining_width = stringWidth(prev[break_idx + 1:], BODY_FONT_OBLIQUE, FOOTER_FONT_SIZE)
                line1_width = label_width + new_width
                
                # if this new width fits, then split here, else continue
                if line1_width <= max_width:
                    split_point = break_idx
                    line2 = prev[split_point:].strip().upper()
                    break
        
        # different offsets based on if line was split or not
        if split_point == None:
            offset = total_width/2
        else:
            offset = line1_width/2
            
        # calculating and displaying the first line of the prev day's word
        pt1_x = (WIDTH/2) - offset
        pt2_x = pt1_x + pt1_width
        pt3_x = pt2_x + pt2_width
        prev_x = pt3_x + pt3_width

        if is_clue:
            pt1_y = pt2_y = pt3_y = prev_y = clue_y - FOOTER_SPACING
        else:
            pt1_y = pt2_y = pt3_y = prev_y = PUZZLE_TOP_Y - ((num_lines - 1) * (TRIANGLE_HEIGHT + BOX_LEN) 
                                                             + ((num_lines - 1) * LINE_SPACING)
                                                             + FOOTER_FONT_SIZE
                                                             + FOOTER_SPACING)

        # setting font for pt1 ("Yesterday's ")
        c.setFont(BODY_FONT, FOOTER_FONT_SIZE)
        c.drawString(pt1_x, pt1_y, pt1)

        # setting font for pt2 ("P.A.S.S")
        c.setFont(BODY_FONT_BOLD, FOOTER_FONT_SIZE)
        c.drawString(pt2_x, pt2_y, pt2)

        # setting font for pt3 ("WORDS: ")
        c.setFont(BODY_FONT, FOOTER_FONT_SIZE)
        c.drawString(pt3_x, pt3_y, pt3)

        # setting font for prev (last proverb)
        c.setFont(BODY_FONT_OBLIQUE, FOOTER_FONT_SIZE)
        
        # draw depending on 
        if split_point == None:
            c.drawString(prev_x, prev_y, prev)
        else:
            c.drawString(prev_x, prev_y, prev[:split_point])
            
        # draw second line if necessary
        if split_point:
            offset2 = remaining_width/2
            line2_x = (WIDTH/2) - offset2
            line2_y = pt1_y - FOOTER_SPACING
            
            c.drawString(line2_x, line2_y, line2)
            
def collapse_spaces(arr):
    for i, s in enumerate(arr):
        arr[i] = re.sub(r'\s+', ' ', s).strip()
    return arr

def draw_description(c):
    line1 = ["Determine the ", "P", "roverb, ", "A", "dage, ", "S", 
             "aying, or ", "S", "aw by converting the triangled numbers"]
    bold = [False, True, False, True, False, True, False, True, False]
    line_2 = "to letters in the connecting squares using the corresponding circular alphanumeric key."
    
    line1_widths = []
    for i, segment in enumerate(line1):
        if bold[i]:
            line1_widths.append(stringWidth(segment, BODY_FONT_BOLD, DESCRIPTION_FONT_SIZE))
        else:
            line1_widths.append(stringWidth(segment, BODY_FONT, DESCRIPTION_FONT_SIZE))
    
    line1_width = sum(line1_widths)
    line2_width = stringWidth(line_2, BODY_FONT, DESCRIPTION_FONT_SIZE)
    
    line1_x = (WIDTH/2) - (line1_width/2)
    line2_x = (WIDTH/2) - (line2_width/2)
    
    line1_y = DESCRIPTION_TOP_Y - 10 # 10 is param
    line2_y = line1_y - BODY_FONT_SIZE - LINE_SPACING/4 # denom is tunable
    
    # setting font to body
    c.setFont(BODY_FONT, DESCRIPTION_FONT_SIZE)
    
    # draw all of line 1
    for i, segment in enumerate(line1):
        if bold[i]:
            # setting font to bold
            c.setFont(BODY_FONT_BOLD, DESCRIPTION_FONT_SIZE)
        else:
            # setting font to normal
            c.setFont(BODY_FONT, DESCRIPTION_FONT_SIZE)
            
        c.drawString(sum(line1_widths[:i]) + line1_x, line1_y, segment)
    
    # draw line 2
    c.drawString(line2_x, line2_y, line_2)

def draw_title_author(c):
    part1, part2 = "P.A.S.S.", "WORDS"
    author = "BY: TC Richardson"
    
    part1_width = stringWidth(part1, BODY_FONT_BOLD, TITLE_LARGE_FONT_SIZE)
    part2_width = stringWidth(part2, BODY_FONT, TITLE_NORMAL_FONT_SIZE)
    author_width = stringWidth(author, BODY_FONT, AUTHOR_FONT_SIZE)
    
    title_width = part1_width + part2_width
    offset = (WIDTH/2) - (title_width/2)
    
    part1_x = offset
    part2_x = offset + part1_width
    
    part1_y = part2_y = DESCRIPTION_TOP_Y + DESCRIPTION_FONT_SIZE + TITLE_SPACING # tunable multiplier
    
    author_x = (WIDTH - MARGIN) - author_width
    author_y = DESCRIPTION_TOP_Y + DESCRIPTION_FONT_SIZE * 1.00 # tunable multiplier
    
    # setting font to bold, large title font size
    c.setFont(BODY_FONT_BOLD, TITLE_LARGE_FONT_SIZE)
    c.drawString(part1_x, part1_y, part1)
    
    # setting font to normal title
    c.setFont(BODY_FONT, TITLE_NORMAL_FONT_SIZE)
    c.drawString(part2_x, part2_y, part2)
    
    # setting font to normal
    c.setFont(BODY_FONT, AUTHOR_FONT_SIZE)
    c.drawString(author_x, author_y, author)

def draw_logo(c):
    lines = [["P.", "roverb"],
            ["A.", "dage"],
            ["S.", "aying"],
            ["S.", "aw"],
            ["W"],
            ["O"],
            ["R"],
            ["D"],
            ["S"]]
    
    bold = [[True, False],
            [True, False],
            [True, False],
            [True, False],
            [False],
            [False],
            [False],
            [False],
            [False]]
    
    # align to top of title
    logo_top_y = DESCRIPTION_TOP_Y + DESCRIPTION_FONT_SIZE + TITLE_SPACING + (TITLE_LARGE_FONT_SIZE - LOGO_LARGE_FONT_SIZE)
    
    for i, line in enumerate(lines):
        # squeeze in y coord for formatting
        y_coord = logo_top_y - (i * LOGO_LARGE_FONT_SIZE) * 0.8 # tunable param
        if len(line) == 1:
            c.setFont(BODY_FONT, LOGO_LARGE_FONT_SIZE)
            c.drawString(PADDING, y_coord, lines[i][0])
        else:
            ch_width = stringWidth(lines[i][0], BODY_FONT_BOLD, LOGO_LARGE_FONT_SIZE)
            
            # draw large letter
            c.setFont(BODY_FONT_BOLD, LOGO_LARGE_FONT_SIZE)
            c.drawString(PADDING, y_coord, lines[i][0])
            
            # draw rest of word
            c.setFont(BODY_FONT, LOGO_NORMAL_FONT_SIZE)
            c.drawString(PADDING + ch_width, y_coord, lines[i][1])

def check_log_directory(log_directory):
    """ Ensure the log directory exists, create if it doesn't. """
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        print(f"Created log directory at: {log_directory}")
    else:
        print(f"Log directory already exists at: {log_directory}")

def open_pdf(filepath):
    try:
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", filepath], check=True)
        elif sys.platform.startswith('linux'):
            subprocess.run(["xdg-open", filepath], check=True)
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"Failed to open file: {e}")

def generate_puzzle(filename, proverb, clue='', prev='', reveal_letters=[]):
    
    # initialize file structure if not existing
    FOLDER = setup_file_structure()
    
    # create canvas in correct folder
    filepath = FOLDER + '/' + filename
    c = canvas.Canvas(filepath, pagesize=letter)

    # randomize letters within circles
    randomize()

    # collapses all spaces into single space
    proverb, clue, prev = collapse_spaces([proverb, clue, prev])
    # removing special characters and extra spaces, uppercasing
    proverb, n = clean_proverb(proverb)
    
    # checking that proverb exists
    if n == 0:
        raise ValueError("Proverb must be of length at least 1.")
    
    # setting font for body
    c.setFont(BODY_FONT_BOLD, BODY_FONT_SIZE)
    
    # intervals of the form (start, end) for each generated line
    line_intervals = separate_lines(proverb, n) 
            
    # splitting up proverb into lines
    lines = []
    line_offsets = [] # to find index of each char in original proverb (without removing trailing spaces) 
    num_lines = 0
    for i,j in line_intervals:
        lines.append(proverb[i:j])
        line_offsets.append(i)
        num_lines += 1
    
    # draw a rectangle and triangle for each letter
    draw_boxes_triangles(c, lines, line_offsets, reveal_letters)

    # draw predefined circles
    draw_circles(c)

    # draw logo
    draw_logo(c)
    
    # draw title and author
    draw_title_author(c)
    
    # drawing top description
    draw_description(c)
    
    # drawing footer (clue + prev answer)
    draw_footer(c, clue, prev, num_lines)
    
    # add proverb and date/time to CSV file log.csv
    log_filepath = FOLDER + '/logs/' 
    check_log_directory(log_filepath)
    log_filepath += LOG_FILENAME

    reveal_letters_string = ','.join([str(i) for i in reveal_letters])
    log_proverb(''.join(proverb), filename, clue, reveal_letters_string, log_filepath)

    c.showPage()
    c.save()

    open_pdf(filepath)

def get_user_input():
    # create main window
    root = tk.Tk()
    root.title("Puzzle Parameters")

    # function to handle button click
    def on_submit():
        global DATA_SUBMITTED

        filename = filename_field.get().strip()
        proverb = proverb_field.get().strip()
        clue = clue_field.get().strip()
        prev = prev_field.get().strip()
        integer_list = reveal_letters.get().strip().split(',') # split string into a list

        errors = []

        if not filename:
            errors.append("Filename is required")
        elif not re.search(PDF_PATTERN, filename, re.IGNORECASE):
            errors.append("Filename must end in \".pdf\".")
        
        if not proverb:
            errors.append("Proverb is required.")

        try:
            # if the field is empty
            if len(integer_list) == 1 and '' in integer_list:
                integer_list = []
            else:
                integer_list = [int(num.strip()) for num in integer_list]
        except ValueError:
            errors.append("Please enter valid integers separated by commas.")

        if errors:
            messagebox.showerror("Validation Error(s)", "\n".join(errors))
            return
        
        messagebox.showinfo("Puzzle Created", f"proverb: {proverb}\nfilename: {filename}")
        user_input_data["filename"] = filename
        user_input_data["proverb"] = proverb
        user_input_data["clue"] = clue
        user_input_data["prev"] = prev
        user_input_data["integers"] = integer_list
        # mark data as submitted
        DATA_SUBMITTED = True

        root.destroy()

    # Configure the padding of the window
    root['padx'] = 20  # Add horizontal padding to the window
    root['pady'] = 20  # Add vertical padding to the window

    tk.Label(root, text="Enter PDF Filename (REQUIRED)").pack()
    filename_field = tk.Entry(root, width=70)
    filename_field.pack()

    tk.Label(root, text="Enter Proverb (REQUIRED)").pack()
    proverb_field = tk.Entry(root, width=70)
    proverb_field.pack()

    tk.Label(root, text="Enter Clue (OPTIONAL)").pack()
    clue_field = tk.Entry(root, width=70)
    clue_field.pack()

    tk.Label(root, text="Enter Previous Day's Answer (OPTIONAL)").pack()
    prev_field = tk.Entry(root, width=70)
    prev_field.pack()

    tk.Label(root, text="Enter Indices of Letters to Reveal (comma-separated integers, OPTIONAL):").pack()
    reveal_letters = tk.Entry(root, width=70)
    reveal_letters.pack()

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.pack()

    root.mainloop()

if __name__ == '__main__':
    get_user_input()
    if DATA_SUBMITTED:
        generate_puzzle(filename=user_input_data["filename"],
                        proverb=user_input_data["proverb"],
                        clue=user_input_data["clue"],
                        prev=user_input_data["prev"],
                        reveal_letters=user_input_data["integers"])
    






