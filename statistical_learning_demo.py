#!/usr/bin/env python
# written by Tuan (Tony) Lam
# version 1.0 - June 16, 2021
"""
This module is designed as a demonstration of statistical learning from a
pseudolanguage. The sound files were originally created by Carla Hudson Kam.
The text_wrap_blit function was modified from a similar function in
TextPresenter.py posted on git by imarevic (Ivan Maravic). The original source
can be found at: https://github.com/imarevic/psy_python_course/blob/master/notebooks/Chapter8/TextPresenter.py

The program first presents instructions to the study followed by training audio.
After presentation of the audio, participants are presented with 8 test items in
which they here two possible words from the language, or which one of them is
correct. They must indicate the correct response with the shift keys.
"""
# import pygame and other required packages
import pygame
import os
import csv
from tkinter import Tk
from random import shuffle
from itertools import zip_longest
from collections import OrderedDict

# set to True or False to debug. Debug will skip training and do 2 test trials
debug = True

# setting to True will randomize the audio files. False will go in order.
randomize = True
"""
The following lines set up the folder and path depedencies. The program expects
three subfolders named 'demo_audio', 'demo_results', and 'instructions'.
Inside 'demo_audio' are the training file ('TrainingFile.wav') and the test
files which are all named Q*.wav where * is an number from 1:8. The instructions
folder should contain a file named 'welcome.txt' which contains the main
instructions for the experiment. The 'demo_results' folder is initially empty
but will fill up with output in the form of .csv files as more participants
complete the task.
"""

# name of required subfolders
audio_folder = 'demo_audio'
results_folder = 'demo_results'
instructions_folder = 'instructions'

# get current working directory
cwd = os.path.abspath(os.curdir)

# creates path to audio folder which is currently named demo3_audio
audio_path = os.path.join(cwd,audio_folder)
# print directory of parent folder
audio_dir = os.listdir(audio_path)

# list to hold names of test audio files
audio_files = []
# fills the audio_files list with all of the test audio file names.
for file in audio_dir:
    # checks audio_dir for sound files beginning with 'Q' (indicating test file)
    if file.endswith('.wav') and file.startswith('Q'):
        audio_files.append(file)

audio_files.sort() # sorts the audio files alphabetically
if randomize: # randomizes order of audio_files items if set to True
    shuffle(audio_files)
# print(audio_files)
num_af = len(audio_files) # count number of test audio_files

# specify the training audio file full path name
training_file = os.path.join(audio_path,'TrainingFile.wav')

# creates path to welcome.txt which should be a subfolder named instructions
instruction_file = os.path.join(cwd, instructions_folder, 'welcome.txt')

# creates path to the results folder to be used when writing results
results_path = os.path.join(cwd,results_folder)

# used to get screen dimensions
root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

"""
=== define global pygame program parameters in a dict ===
this ensures that they are accessible in each function
"""
exp_globals = {"bg_color": (180, 180, 180), # bg is light grey
              "text_color": (0, 0, 0), # text is green
              "screen_size": (screen_width, screen_height), # set screen screenSize
              "FPS": 60, # frames per second
              "font": None, # sets font type
              "screen": None, # placeholder for screen instance
              "screen_rect": None, # placeholder for screen rectangle
              "window_caption": 'Demo 3', # caption for pygame window
}
answer_key = {"Q1.wav": 1,
              "Q2.wav": 2,
              "Q3.wav": 2,
              "Q4.wav": 1,
              "Q5.wav": 1,
              "Q6.wav": 2,
              "Q7.wav": 1,
              "Q8.wav": 2
}

results_out = OrderedDict([("PID", None), # participant number
                           ("trial_num", []), # trial number
                           ("audio_files", []), # trial audio
                           ("responses", []), # trial response
                           ("rt", []), # trial reaction time
                           ("accuracy", None) # trial accuracy
])

def run_expt():
    """runs the experiment."""
    # initialize pygame and font
    init_pygame(exp_globals["screen_size"], exp_globals["FPS"])
    # show main instructions for the experiment.
    load_instructions()
    # if debugging, skip the training audio, otherwise play training audio
    if debug:
        pass
    else:
        # play the training audio
        play_training(training_file)

    # a wait screen before starting test trials
    press_to_continue()
    # start presentation of n trials where n is the number of test audio files
    start_presentation(num_af)
    # write results to a file
    write_responses(results_out)
    # exit Experiment
    pygame.mixer.quit()
    pygame.quit()

def init_pygame(screen_size: tuple, FPS: int = 60):
    """
    initializes pygame and screen variables. Also initializes the mixer for
    playing sound.
    arg1 screen_size: tuple representing the X and Y dimensions of the screen.
    arg2 FPS: static framerate which defaults to 60 fps.
    """
    pygame.init()
    pygame.display.set_caption(exp_globals["window_caption"])

    # set the initial screen ID for the new display
    exp_globals["screen"] = pygame.display.set_mode(exp_globals["screen_size"])
    exp_globals["screen_rect"] = exp_globals["screen"].get_rect()

    # scale font size to screen dimensions
    font_size = round(exp_globals["screen_size"][0]/1920*50)
    exp_globals["font"] = pygame.font.SysFont("Arial", font_size)
    pygame.display.flip()

    # set frame rate
    clock = pygame.time.Clock()
    clock.tick(exp_globals["FPS"])

    # initiate mixer for pygame audio
    pygame.mixer.init()

def load_instructions():
    """
    Loads main experiment instructions from a text file named welcome.txt which
    is located in a subfolder named instructions. The instructions are then
    blipped onto the screen using text_wrap_blit to wrap the text as needed. The
    particpants have to press ENTER or RETURN to continue with the experiment.
    """
    with open(instruction_file, 'r') as file:
        infile = file.read()

    # fill background
    exp_globals["screen"].fill(exp_globals["bg_color"])

    # blit wrapped text for instructions to main screen
    text_wrap_blit(exp_globals["screen"], infile, exp_globals["font"], exp_globals["screen_size"][0] - 100, (50, 50),exp_globals["text_color"])
    pygame.display.flip()
    pygame.time.wait(500) # wait at least 500 ms before allowing one to continue

    # Loop to wait for participants to press SPACE before moving on
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def play_training(training_file: str):
    """
    This function is used to play the training audio file 'TrainingFile.wav'
    which is located in the demo_audio subfolder. It will play the file until
    it ends and then stops. If debug is set to True, training will be skipped.
    training_file: string representing full path to training file
    """
    # load training file
    training_audio = pygame.mixer.Sound(training_file)

    # display training instructions
    instructions = 'Please listen to the training audio.'

    # render text_item
    text_item = exp_globals["font"].render(instructions, True, exp_globals["text_color"], exp_globals["bg_color"])
    # get text item rect
    text_item_rect = text_item.get_rect()
    # place text at center of the screen
    text_item_rect.center = exp_globals["screen_rect"].center

    # fill background
    exp_globals["screen"].fill(exp_globals["bg_color"])
    # draw to backbuffer
    exp_globals["screen"].blit(text_item, text_item_rect)
    pygame.display.flip()

    # play audio_file until end
    playing = training_audio.play()
    while playing.get_busy():
        pygame.time.wait(60)
    # close audio_file
    training_audio.stop()

def ISI(duration: int = 500):
    """
    Used to draw an inter stimulus interval.
    duration: int representing interstimulus interval duration in milliseconds
    """
    # fill background
    exp_globals["screen"].fill(exp_globals["bg_color"])
    pygame.display.flip()

    # wait for ISI, default duration = 500
    pygame.time.wait(duration)

def press_to_continue():
    # display instructions
    instructions = 'Press SPACE to begin test trials.'

    # render textItem
    text_item = exp_globals["font"].render(instructions, True, exp_globals["text_color"], exp_globals["bg_color"])
    # get text item rect
    text_item_rect = text_item.get_rect()
    # place at center of the screen
    text_item_rect.center = exp_globals["screen_rect"].center

    # fill background
    exp_globals["screen"].fill(exp_globals["bg_color"])
    # draw to backbuffer
    exp_globals["screen"].blit(text_item, text_item_rect)
    pygame.display.flip()
    pygame.time.wait(500) # wait at least 500 ms before allowing one to continue

    # Loop to wait for participants to press SPACE before moving on
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

# wrapper function that calls the audio function and the responses function.
def start_presentation(n_trials: int = 2):
    """
    Wrapper function that calls the play_audio function and the get_responses
    function. It starts with an ISI, followed by a test trial. Afterwards,
    participants must make a response. If debug is set, then it only does two
    test trials.
    n_trials: int represents the number of trials based on audio_files list
    """
    if debug:
        n_trials = 2
    for m in range(n_trials):
        if(audio_files == []):
            pass
        else:
            ISI()
            results_out["audio_files"].append(audio_files[m])
            af = os.path.join(audio_path,audio_files[m])
            # print(af)
            play_audio(af, m+1)
            get_responses(m+1) # pass m + 1 in a trial number

def play_audio(audio_file: str, trial_num: int):
    """
    This function is designed to play the test audio file k times and then stop.
    It also takes in an int as a trial number for display.
    audio_file: str representing the full path to an audio file.
    trial_num: int representing current trial number.
    """
    # load audio audio_file
    speechfile = pygame.mixer.Sound(audio_file)

    # display instructions
    instructions = 'Test Trial ' + str(trial_num)

    # render textItem
    text_item = exp_globals["font"].render(instructions, True, exp_globals["text_color"], exp_globals["bg_color"])
    # get text item rect
    text_item_rect = text_item.get_rect()
    # place at center of the screen
    text_item_rect.center = exp_globals["screen_rect"].center

    # fill background
    exp_globals["screen"].fill(exp_globals["bg_color"])
    # draw to backbuffer
    exp_globals["screen"].blit(text_item, text_item_rect)
    pygame.display.flip()

    # play audio_file k times pausing for 1 second between
    playing = speechfile.play()
    # checks to see if the file is still playing and stops when it's done
    while playing.get_busy():
        pygame.time.wait(60)
    # stop audio_file
    speechfile.stop()
# record response
def get_responses(trial_num: int):
    """
    This function is designed to wait for a keyboard event where people indicate
    either the first or second sound as the correct sound item. Pressing the
    left SHIFT key indicates sound1. Pressing the right SHIFT key indicates
    sound2. It then stores this response in results_out["responses"].
    trial_num: int representing current trial
    """
    # display instructions
    instructions1 = "LEFT SHIFT for sound 1."
    instructions2 = " RIGHT SHIFT for sound 2."
    instructions_center = "Which sound was the real word?"

    # render textItems for response instructions
    text_item1 = exp_globals["font"].render(instructions1, True, exp_globals["text_color"], exp_globals["bg_color"])
    text_item2 = exp_globals["font"].render(instructions2, True, exp_globals["text_color"], exp_globals["bg_color"])
    text_item3 = exp_globals["font"].render(instructions_center, True, exp_globals["text_color"], exp_globals["bg_color"])

    # get text item rects
    text_item_rect1 = text_item1.get_rect()
    text_item_rect2 = text_item2.get_rect()
    text_item_rect3 = text_item3.get_rect()

    # place at text rects at center of the left and right screen
    text_item_rect1.center = (exp_globals["screen_rect"].center[0] -exp_globals["screen_size"][0]/4,exp_globals["screen_rect"].center[1])
    text_item_rect2.center = (exp_globals["screen_rect"].center[0] + exp_globals["screen_size"][0]/4,exp_globals["screen_rect"].center[1])
    text_item_rect3.center = (exp_globals["screen_rect"].center[0], exp_globals["screen_rect"].center[1]/2)
    # fill background
    exp_globals["screen"].fill(exp_globals["bg_color"])

    # draw text to backbuffer
    exp_globals["screen"].blit(text_item1, text_item_rect1)
    exp_globals["screen"].blit(text_item2, text_item_rect2)
    exp_globals["screen"].blit(text_item3, text_item_rect3)
    pygame.display.flip()
    start_time = pygame.time.get_ticks()
    # waits for a response and then records it to exp_globals.
    pygame.event.clear()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Respond to a keypress LSHIFT and RSHIFT
                if event.key == pygame.K_LSHIFT:
                    click_time = pygame.time.get_ticks()
                    rt = click_time - start_time
                    results_out["trial_num"].append(trial_num)
                    results_out["responses"].append(1)
                    results_out["rt"].append(rt)
                    waiting = False
                elif event.key == pygame.K_RSHIFT:
                    click_time = pygame.time.get_ticks()
                    rt = click_time - start_time
                    results_out["trial_num"].append(trial_num)
                    results_out["responses"].append(2)
                    results_out["rt"].append(rt)
                    waiting = False

def write_responses(results: dict):
    """
    This function is used to write the results to a .csv file. It first looks at
    the responses and compares them to the correct responses in exp_globals. It
    then calculates the accuracy of each response and saves this. It then checks
    the results folder for files. PID will be file count + 1. It then writes the
    results as demo_results#.csv where # represents the PID number. Therefore,
    this folder should not include any other files except results output files.
    results: dictionary representing the trial by trial data and results.
    """
    accuracy = []
    for k in range(len(results["responses"])):
        af = results["audio_files"][k]
        if results["responses"][k] == answer_key[af]:
            accuracy.append('CORRECT')
        else:
            accuracy.append('INCORRECT')
    results["accuracy"] = accuracy

    # counts the files in the results folder. Then sets PID to count + 1.
    results_count = 0
    results_dir = os.listdir(results_path)
    for file in results_dir:
        # checks results_dir for .csv files (indicating previous participants)
        if file.endswith('.csv'):
            results_count += 1
    PID = results_count + 1
    results["PID"] = [PID]*len(accuracy)
    new_results = os.path.join(results_path,'results' + str(PID) + ".csv")
    with open(new_results, 'w') as file:
        # create writer
        writer = csv.writer(file, delimiter = ",")
        # write data keys
        writer.writerow(results.keys())
        # write values row wise
        writer.writerows(zip_longest(*results.values())) # dict list values are unpacked first

    # blit the results to the screen for 5 seconds before ending
    blit_results(accuracy)

def blit_results(accuracy: list):
    """
    Function used to blit the results to the screen. It will display the number
    of correct items out of the number of trials completed.
    accurary: list representing representing correctness of each response
    """
    # count total number of items
    num_items = len(accuracy)
    # counting number of correct items, 0 before counting.
    num_correct = 0
    for item in accuracy:
        if item == 'CORRECT':
            num_correct += 1
    # render text items for results output and blits to center of screen
    results_text = "You got ( " + str(num_correct) + " / " + str(num_items) + " )  correct."
    results_item = exp_globals["font"].render(results_text, True, exp_globals["text_color"], exp_globals["bg_color"])
    results_item_rect = results_item.get_rect()
    results_item_rect.center = (exp_globals["screen_rect"].center[0], exp_globals["screen_rect"].center[1])

    # fill background
    exp_globals["screen"].fill(exp_globals["bg_color"])

    # draw text to backbuffer
    exp_globals["screen"].blit(results_item, results_item_rect)
    pygame.display.flip()

    # Loop to wait for SPACE bar or wait 5000 ms before ending
    waiting = True
    start_time = pygame.time.get_ticks()
    while waiting:
        if pygame.time.get_ticks() - start_time > 5000:
            waiting = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False


def text_wrap_blit(surface: pygame.Surface, text: str, font: str, width: int, start_pos: tuple, color: tuple, after_spacing: int = 0, antialiasing: bool = True):
    """
    The function blits text on a surface with multiple lines while wrapping text
    onto new line whenever it exeeds the width that is specified. Modified version of text_object_blit_wrapped from TextPresenter.py to remove
    unneccessary height argument and add the optional arguments after_spacing
    and antialiasing.
    surface: pygame.surface object
    text: string of text to be wrapped and blitted
    width: int representing pixel width of text to be blitted
    start_pos: tuple representing starting position as (X, Y)
    color: tuple representing RGB color
    after_spacing: int representing pixel spacing after new lines
    antialiasking: bool, if True, there will be smoothing of text
    """
    # get list of words row wise
    words = [word.split(' ') for word in text.splitlines()]
    # get size of spaces
    space = font.size(' ')[0]
    # unpack tuple for x and y coordinates of the text object
    x_pos, y_pos = start_pos

    # iterate over words and lines
    for line in words:
        for word in line:
            # create word surface and get width and height of current word
            word_surface = font.render(word, antialiasing, color)
            word_width, word_height = word_surface.get_size()

            # check if new line needs to be started
            if x_pos + word_width >= width:
                # reset position to new line coordinates
                x_pos = start_pos[0]
                y_pos += word_height + after_spacing

            # blit current word and update position
            surface.blit(word_surface, (x_pos, y_pos))
            x_pos += word_width + space

        # reset positions for each new line
        x_pos = start_pos[0]
        y_pos += word_height

# == start the program == #
if __name__ == '__main__':
    run_expt()
