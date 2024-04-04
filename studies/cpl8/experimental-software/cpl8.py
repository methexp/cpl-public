
from psychopy import core, visual, event, gui
import csv
import sys
import os, statistics, io, math



# define some helpful functions (hats off to Tobias Heycke) ----

def instruct(text, further = "Drücke die Leertaste, um fortzufahren.", pos = (0, 0), keyList = 'space', maxWait = math.inf):
    
    

    stimulus = visual.TextStim(win, text = text + "\n\n\n" + further, pos = pos)
    stimulus.draw()
    win.flip()
    core.wait(.1)
    event.clearEvents()
    
    key_press = event.waitKeys(keyList = keyList, maxWait = maxWait)
    if(key_press is None):
        key_press = "NA"
    return key_press





# create a DlgFromDict

while True:

    info = {
      'Alter': "",
      'Geschlecht':['Bitte geben Sie Ihr Geschlecht an.', 'weiblich', 'männlich', 'divers'],
      'Muttersprache': ['Bitte geben Sie Ihre Muttersprache an.' , 'Deutsch', 'andere'],
      'Farbfehlsichtigkeit': ['Bitte geben Sie an, ob Sie eine Farbfehlsichtigkeit haben.', 'nein', 'ja']}
        
    infoDlg = gui.DlgFromDict(
      dictionary=info,
      title = 'cpl8',
      order = ["Alter", "Geschlecht", "Muttersprache", "Farbfehlsichtigkeit"]
    )
    
    if (info['Alter'] != "") & (info['Geschlecht'] != 'Bitte geben Sie Ihr Geschlecht an.') & (info['Muttersprache'] != 'Bitte geben Sie Ihre Muttersprache an.') & (info["Farbfehlsichtigkeit"] != 'Bitte geben Sie an, ob Sie eine Farbfehlsichtigkeit haben.'):
        break



if infoDlg.OK:  # this will be True (user hit OK) or False (cancelled)
    print(info)
else:
    print('User Cancelled')
    core.quit()



# Setup ----

DEBUG = False

if DEBUG:
    onesec = 1
    win = visual.Window([1920, 1080], monitor = "testMonitor", units = 'pix', fullscr = False, color = [-1, -1, -1])
else:
    onesec = 1
    win = visual.Window([1920, 1080], monitor = "testMonitor", units = 'pix', fullscr = True, color = [-1, -1, -1])



trialclock = core.Clock()
mouse = event.Mouse(visible = False) # hide mouse


# fetch participant id from bash/batch
if len(sys.argv) > 1:
    sid = int(sys.argv[1])
    print("Using sid from parameter.")
else:
    sid = 5
    print("Using default sid = "+ str(sid) + ".")
    
    
# Import special instruction text
dirname = os.path.dirname(__file__)
instructions_file = os.path.join(dirname, "stimuli", "instructions-" + str(sid) + ".txt")
with io.open(instructions_file, mode = "r", encoding = "utf-8") as f: # note that we use the io package to be able to specify encoding
    instruction_text = f.read()
    
sequence_file = os.path.join(dirname, "stimuli", "sequence-" + str(sid) + ".txt")
with open(sequence_file) as f:
    instruction_sequence = f.readlines()

# Import stimulus list
stimulus_file = os.path.join(dirname, "stimuli", "acquisition-" + str(sid) + ".csv")
stimulus_file = open(stimulus_file, newline = '')
hands_file = os.path.join(dirname, "stimuli", "hands-for-exp.png")
hands_digits_file = os.path.join(dirname, "stimuli", "hands-for-exp-digits.png")
attention_file = os.path.join(dirname, "stimuli", "attention.png")


reader = csv.DictReader(stimulus_file, delimiter = ",")

# Prepare data file
data_file = os.path.join(dirname, "data", str(sid) + ".csv")
data_file = open(data_file, newline = "", mode = "a")

data_writer = csv.DictWriter(data_file, fieldnames = ["sid", "bid", "tid", "material", "instructions", "material_order", "stimulus_location", "response_location", "response_time", "response_deadline", "error"])
data_writer.writeheader()



# Prepare demographics file
demographics_file = os.path.join(dirname, "data", "demographics", str(sid)+ ".csv")
demographics_file = open(demographics_file, mode = "a", newline = "")

demographics_writer = csv.DictWriter(demographics_file, fieldnames = ["sid", "age", "gender", "native_language", "impaired_vision"])
demographics_writer.writeheader()
demographics_writer.writerow({
    'sid': sid, "age": info['Alter']
    , 'gender':info['Geschlecht']
    , 'native_language':info["Muttersprache"]
    , 'impaired_vision': info["Farbfehlsichtigkeit"]
})

# Prepare file that holds keys that were pressed during sequence instructions
instruction_data_file = os.path.join(dirname, "data", "instructions-" + str(sid) + ".csv")
instruction_data_file = open(instruction_data_file, mode = "a")


# prepare stimuli
trials_per_block = 144

tid_list = []
stimulus_location = []
pos_x = []
prepared_stimuli = []
response_deadline = []

first_response_location =[]
first_response_time = []

for row in reader:
    tid = int(row['tid'])
    sl = int(row['stimulus_location'])
    material = row["material"]
    instructions = row["instructions"]
    material_order = row["material_order"]
    
    
    tid_list.append(tid)
    stimulus_location.append(sl)
    
    response_deadline.append(float(row['response_deadline']))
    
    # stimulus creation
    x_coord = row['pos_x']
    pos_x.append(x_coord)
    
    
    stimulus = visual.Rect(win, size = (72,72), pos = (x_coord, 0), fillColor=[0, 0, 0], lineColor = [0, 0, 0])
    stimulus.draw()
    prepared_stimuli.append(stimulus)

instruction_stimuli = []
for i in range(0, 6):
    
    x_coord = -360 + i * 144
    
    stimulus = visual.Rect(win, size = (72,72), pos = (x_coord, 0), fillColor=[0, 0, 0], lineColor = [0, 0, 0])
    
    instruction_stimuli.append(stimulus)


stimulus_array = []

x_coords = [-360, -216, -72, 72, 216, 360]
for i in range(0, 6):
    tmpstim = visual.Rect(win, size = (72,72), pos = (x_coords[i], 0), fillColor = [-1, -1, -1], lineColor = [-.9, -.9, -.9])
    stimulus_array.append(tmpstim)


def draw_array(stimulus_array):
    for i in range(len(stimulus_array)):
        stim = stimulus_array[i]
        stim.draw()


in_words = []
for i in range(trials_per_block + 1):
    in_words.append(str(i) + "-mal")
in_words[slice(1, 13)] = ["einmal", "zweimal", "dreimal", "viermal", "fünfmal", "sechsmal", "siebenmal", "achtmal", "neunmal", "zehnmal", "elfmal", "zwölfmal"]





too_fast = visual.TextStim(win, text = "Bitte reagiere erst dann, wenn das weiße Quadrat angezeigt wird.", pos = (0, -120))
too_slow = visual.TextStim(win, text = "Zu langsam! Bitte versuche, schneller zu reagieren.", pos = (0, -120))
error_feedback = visual.TextStim(win, text = "Falsche Taste!", pos = (0, -120))
black = visual.Rect(win, size = [1920, 1080], fillColor = [-1, -1, -1], lineColor = [-1, -1, -1])

responses = {"y": 1, "x": 2, "c": 3, "comma":4, "period":5, "minus":6}
block_length = 144
stimulus_onset = .25

errors = []
countdown = []

for i in range(5):
    stim = visual.TextStim(win, text = str(5-i))
    countdown.append(stim)
    
    
setup_drawing = visual.ImageStim(win = win, image = hands_file, pos = (0, -300))
setup_drawing_digits = visual.ImageStim(win = win, image = hands_digits_file, pos = (0, -300))

attention = visual.ImageStim(win = win, image = attention_file, pos = (0, 200))


black.draw()
win.flip()


# Experiment proper ----


n_blocks = 12
block_number = 1
n_too_slow = 0
n_too_fast = 0
n_error = 0

instruct(str(sid), further = "")

instruct("Herzlich willkommen und vielen Dank, dass du an unserer Studie teilnimmst! Wir untersuchen den Zusammenhang zwischen räumlicher Aufmerksamkeit und Reaktionsfähigkeit.\n\nDie Studie wird vollständig am Computer durchgeführt: Lies dir deshalb die folgenden Instruktionen sorgfältig durch und versuche in der anschließenden Experimentalphase, diese so gut es geht zu befolgen.\n\nBevor du in die Experimentalphase startest werden wir dir aber auch noch einmal die Gelegenheit geben, etwaige Fragen mit dem Versuchsleiter bzw. der Versuchsleiterin zu klären.")

while True: # while loop for eventually repeating instructions

    
    setup_drawing.draw()
    instruct("Lege zunächst Ringfinger, Mittelfinger und Zeigefinger deiner linken Hand auf die drei linken Tasten, die auf der Tastatur markiert sind. Lege dann Zeigefnger, Mittelfinger und Ringfinger der rechten Hand auf die drei rechten der markierten Tasten der Tastatur.", pos = (0, 0))

    draw_array(stimulus_array)
    instruct("In jedem Durchgang zeigen wir dir an einer von sechs Positionen des Bildschirms ein Quadrat.", pos = (0, -300))
    draw_array(stimulus_array)
    stim = prepared_stimuli[6]
    stim.draw()
    instruct("Deine Aufgabe besteht darin, möglichst schnell die Position des Quadrats zu erkennen und auf der Tastatur die richtige der sechs markierten Tasten zu drücken.", pos = (0, -300))
    draw_array(stimulus_array)
    stim = instruction_stimuli[0]
    stim.draw()
    instruct("Wenn das Quadrat ganz links angezeigt wird, dann drücke die ganz linke Taste.", pos = (0, -300), keyList = "y", further = "Drücke jetzt diese Taste, um fortzufahren.")
    draw_array(stimulus_array)
    stim = instruction_stimuli[1]
    stim.draw()
    instruct("Wenn das Quadrat an der zweiten Position von links angezeigt wird, dann drücke die zweite Taste von links.", pos = (0, -300), keyList = "x", further = "Drücke jetzt diese Taste, um fortzufahren.")
    draw_array(stimulus_array)
    stim = instruction_stimuli[2]
    stim.draw()
    instruct("Wenn das Quadrat an der dritten Position von links angezeigt wird, dann drücke die dritte Taste von links.", pos = (0, -300), keyList = "c", further = "Drücke jetzt diese Taste, um fortzufahren.")
    draw_array(stimulus_array)
    stim = instruction_stimuli[3]
    stim.draw()
    instruct("Wenn das Quadrat an der dritten Position von rechts angezeigt wird, dann drücke die dritte Taste von rechts.", pos = (0, -300), keyList = "comma", further = "Drücke jetzt diese Taste, um fortzufahren.")
    draw_array(stimulus_array)
    stim = instruction_stimuli[4]
    stim.draw()
    instruct("Wenn das Quadrat an der zweiten Position von rechts angezeigt wird, dann drücke die zweite Taste von rechts.", pos = (0, -300), keyList = "period", further = "Drücke jetzt diese Taste, um fortzufahren.")
    draw_array(stimulus_array)
    stim = instruction_stimuli[5]
    stim.draw()
    instruct("Wenn das Quadrat ganz rechts angezeigt wird, dann drücke die ganz rechte Taste.", pos = (0, -300), keyList = "minus", further = "Drücke jetzt diese Taste, um fortzufahren.")
    
    instruct(text = "Versuche in der folgenden Experimentalphase, immer möglichst schnell mit der entsprechenden Taste auf die Quadrate zu reagieren. Das kann ziemlich anstrengend sein, aber die Untersuchung ist in vierzehn kürzere Blöcke unterteilt, zwischen denen du eine Pause machen kannst.", pos = (0, 0))
    if(row["instructions"]=="sequence revealed"):
        setup_drawing_digits.draw()
        instruct(text = instruction_text, pos = (0, 100))
        for j in range(len(instruction_sequence)):
            draw_array(stimulus_array)
            stim = instruction_stimuli[int(instruction_sequence[j])-1]
            stim.draw()
            out = instruct("Bitte präge dir die Reihenfolge der Quadrate ein.", pos = (0, -300), maxWait = 1, further = "", keyList = ["y", "x", "c", "comma", "period", "minus"])
            instruction_data_file.write(str(out[0]) + "\n")
        if(row["material"]=="probabilistic"):
            instruct("Das Quadrat wird jedoch nicht immer der Reihenfolge folgen:\n\nIn jedem Durchgang wird neu entschieden, ob das Quadrat an der Position angezeigt wird, die der Reihenfolge folgt, oder an einer der anderen Positionen. In 3 von 5 Fällen (also in 60% der Durchgänge) wird das Quadrat der Reihenfolge folgen.")
        else:
            if row["material_order"] == "regular first":
                instruct("Das Quadrat wird jedoch nicht immer der Reihenfolge folgen:\n\nNur in ungeraden Blöcken (also den Blöcken 1, 3, 5, 7, 9, 11 und 13) wird das Quadrat der Reihenfolge folgen. In geraden Blöcken (also den Blöcken 2, 4, 6, 8, 10, 12 und 14) wird das Quadrat an einer zufällig ausgewählten Position erscheinen.")
            else:
                instruct("Das Quadrat wird jedoch nicht immer der Reihenfolge folgen:\n\nNur in geraden Blöcken (also den Blöcken 2, 4, 6, 8, 10, 12 und 14) wird das Quadrat der Reihenfolge folgen. In ungeraden Blöcken (also den Blöcken 1, 3, 5, 7, 9, 11 und 13) wird das Quadrat an einer zufällig ausgewählten Position erscheinen.")
            
    instruct("Zusammenfassung\n\n1.) Lege Ring-, Mittel- und Zeigefinger deiner Hände auf die markierten Tasten der Tastatur und lasse sie dort ruhen.\n2.) Während der Untersuchung wird dir immer ein Quadrat an einer von sechs Stellen des Bildschirms angezeigt.\n3.) Reagiere möglichst schnell auf das Quadrat, indem du die entsprechende Taste auf der Tastatur drückst. Bitte versuche dabei aber auch, nicht allzu viele Fehler zu machen."
    + ("\n4.) Nutze dein Wissen über die Reihenfolge, um die Aufgabe möglichst gut zu bearbeiten." if (row["instructions"]=="sequence revealed") else ""))
    out = instruct("Alles verstanden?", further = "Falls du die Aufgabenstellung noch einmal lesen möchtest, drücke die Leertaste. Wenn du Fragen hast oder dir unsicher bist, ob du die Aufgabe richtig verstanden hast, kannst du dich jetzt auch an die Versuchsleiterin oder den Versuchsleiter wenden. Falls du mit dem Experiment loslegen willst, drücke die 'w'-Taste.", keyList = ['space', 'w'])
    if out==['w']:
        break

instruction_data_file.close()




# Countdown
get_ready= visual.TextStim(win = win, text = "Bitte lege deine Finger auf die markierten Tasten.\nGleich geht es los...", pos = (0, -200))

for i in range(len(countdown)):
    stim = countdown[i]
    get_ready.draw()
    stim.draw()
    win.flip()
    core.wait(1*onesec)




for t in range(len(prepared_stimuli)):
    

    # Prepare stimuli for this trial...
    stimulus = prepared_stimuli[t]
    stimulus.draw() # already draw once because first time might take extra time
    black.draw()
    # but cover everything!
    
    
    # Start the trial...
    draw_array(stimulus_array)
    win.flip()
    event.clearEvents()
    trialclock.reset()
    
    while True:
        present_stimulus = False
        draw_array(stimulus_array)
        
        if trialclock.getTime()>=stimulus_onset:
            # then, add a stimulus
            present_stimulus = True
            stimulus.draw()
        
        win.flip()
        key = event.getKeys(keyList = ["y", "x", "c", "comma", "period", "minus"], timeStamped = trialclock)
        
        if((len(key)>0) & (present_stimulus == False)):
            draw_array(stimulus_array)
            too_fast.draw()
            win.flip()
            core.wait(2*onesec)
            n_too_fast += 1
            break
        
        if ((len(key)>0) & present_stimulus):
            resp = responses[key[0][0]]
            error = int(resp != stimulus_location[t])
            errors.append(error)
            n_error += error
            
            if trialclock.getTime()>(response_deadline[t]+stimulus_onset): # response deadline
                draw_array(stimulus_array)
                attention.draw()
                too_slow.draw()
                win.flip()
                core.wait(1.2*onesec)
                event.clearEvents()
                n_too_slow += 1
                win.flip()
            elif error:
                draw_array(stimulus_array)
                error_feedback.draw()
                win.flip()
                core.wait(0.3*onesec)
                win.flip()
            else:
                win.flip()
            break
            
    # What is done after each trial phase...
            
    if(len(key) == 0):
        data_writer.writerow({
        "sid": sid
        , "bid": block_number
        , "tid": tid_list[t]
        , "material": material
        , "instructions": instructions
        , "material_order": material_order
        , "stimulus_location": stimulus_location[t]
        , "response_deadline": response_deadline[t]
        })
        
    
    # log all key presses
    for k in range(len(key)):
        
        resp = responses[key[k][0]]
        error = int(resp != stimulus_location[t])
        data_writer.writerow({
        "sid": sid
        , "bid": block_number
        , "tid": tid_list[t]
        , "material": material
        , "instructions": instructions
        , "material_order": material_order
        , "stimulus_location": stimulus_location[t]
        , "response_location": responses[key[k][0]]
        , "response_time": round(key[k][1] - stimulus_onset, 4)
        , "response_deadline": response_deadline[t]
        , "error": error
        })
    
    
    # Adds block structure (for breaks, feedback, etc.)
    if (t+1) % block_length == 0:
        if (t+1) < len(prepared_stimuli):
            # feedback
            msg_text = "Das war der " + str(block_number) + ". Block."
            
            if n_too_slow > 8:
                msg_text += "\n\nDu hast in diesem Block " + str(in_words[n_too_slow]) + " zu langsam reagiert."
                msg_text += " Bitte versuche, im kommenden Block schneller zu reagieren."
                
            if n_error > 50:
                msg_text += "\n\n Du hast in diesem Block " + str(in_words[n_error]) + " mit der falschen Taste reagiert."
                msg_text += "Bitte versuche, weniger Fehler zu machen."
                        
            block_number += 1
            n_too_fast = 0
            n_too_slow = 0
            n_error = 0
            
            # adaptive response deadline
            # if statistics.mean(errors) <.2: mean() needs at least one observation
            #     shift_response_deadline += -.05
                
            #errors = []
            instruct(text = msg_text, further = "Drücke die Leertaste, um mit dem nächsten Block zu beginnen.")
            
            # Countdown
            for i in range(len(countdown)):
                stim = countdown[i]
                stim.draw()
                get_ready.draw()
                win.flip()
                core.wait(1*onesec)
        
        event.clearEvents()


# Thank you and goodbye
instruct(text = "Geschafft, das war der letzte Block!\n\nBitte melde dich jetzt wieder bei der Versuchsleitung. Es folgt noch eine kurze Nachbefragung.", further = "", keyList = "q")



# Closing ----
data_file.close()
win.close()
core.quit()
