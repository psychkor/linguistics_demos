# Statistical Learning
This demo is written fully in Python 3 using pygame and tkinter. It is a demonstration of statistical learning using nonsense syllables modeled after Saffran, Aslin, and Newport (1996). 

Included in the demo is one Python module, nine sound files, and an instructions file. The sound files were originally created by Carla Hudson Kam and are provided with permission for this demo. They consist of a 1 minute and 43 seconds long training audio file and eight short (< 10 seconds) test files. These files are stored under a folder named 'demo_audio'. The are also participant instructions stored in a file named 'welcome.txt' which is located in the instructions subfolder. 

To run the program correctly, you will need to copy the entire file structure. The python module statistical_learning_demo.py will need to be in your main folder. You will need to have subfolders named 'demo_audio', 'demo_results', and 'instructions'. The subfolder 'demo_audio' and 'instructions' will need to contain the sound files and the instruction files respectively. Upon successfully completing the experiment, the program will output a file results file titled 'results#.csv' where # is the participant number determined by the number of .csv files in the 'demo_results' folder.

In order to run statistical_learning_demo.py you may need to install pygame, tkinter, and csv.
