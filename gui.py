from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import twitter2
import time
import inspect
from PIL import Image, ImageTk
import os

def getDefaultArgs(func):
    args, varargs, keywords, defaults = inspect.getargspec(func)
    return dict(zip(args[-len(defaults):], defaults))

def defaultSettings(*args):
    defaultArgs = getDefaultArgs(twitter2.fetch_tweets)
    lang.set(defaultArgs['lang'])
    nTweets.set(defaultArgs['nTweets'])
    nFlush.set(defaultArgs['nFlush'])
    media.set(defaultArgs['media'])
    mSize.set(defaultArgs['mSize'])
    viewMedia.set(defaultArgs['viewMedia'])
    saveMedia.set(defaultArgs['saveMedia'])
    workDir.set(defaultArgs['workDir'])
    saveLog.set(defaultArgs['saveLog'])
    logName.set(defaultArgs['logName'])

def enableNav(*args):
    global current
    global total
    global prevButton
    global nextButton
    if current.get() <= 0:
        prevButton.configure(state='disabled')
    elif current.get() >= total-1:
        nextButton.configure(state='disabled')
    else:
        nextButton.configure(state='enabled')
        prevButton.configure(state='enabled')

def enableButton(*args):
    if query.get():
        fetchButton.configure(state='normal')
    else:
        fetchButton.configure(state='disabled')

def callbackViewMedia():
    if viewMedia.get() == "True":
        mSizeCombo.configure(state="readonly")
    else:
        mSizeCombo.configure(state="disabled")

def callbackSaveMedia():
    if saveMedia.get() == "True":
        workDirEntry.configure(state="normal")
        workDir.set(time.strftime("%d_%b_%Y_%H.%M.%S"))
    else:
        workDirEntry.configure(state="disabled")
        workDir.set("cache")

def callbackLogEntry():
    if saveLog.get() == "True":
        logNameEntry.configure(state="normal")
    else:
        logNameEntry.configure(state="disabled")

def str2Bool(str):
    if str == "True":
        result = True
    else:
        result = False
    
    return result

tweets = None
total = 0
photoDir = ""

def fetch(*args):
    try:
        # Reset every time we fetch
        global tweets
        tweets = None
        global total 
        total = 0
        global photoDir 
        photoDir = ""

        bar.start()
        query_ = query.get()
        lang_ = lang.get()
        nTweets_ = int(nTweets.get())
        nFlush_ = int(nFlush.get())
        media_ = str2Bool(media.get())
        mSize_ = mSize.get()
        saveMedia_ = str2Bool(saveMedia.get())
        viewMedia_ = str2Bool(viewMedia.get())
        workDir_ = workDir.get()
        saveLog_ = str2Bool(saveLog.get())
        logName_ = logName.get()

        # Actually fetch the tweets
        result = twitter2.fetch_tweets(query_, lang_, nTweets_, nFlush_, media_, 
                              mSize_, saveMedia_, viewMedia_, workDir_,
                              saveLog_, logName_)
        bar.stop()
        tweets = result[0]
        total = result[1]
        photoDir = result[2]

        #initViewer(stream, total, photoDir)

    except ValueError:
        pass

mediaLabel = None
current = 0
vName = ""
vHandle = ""
vFavCount = ""
vRtCount = ""
vHasht = ""
vText = ""
nextButton = None
prevButton = None


def initViewer():

    # reset global count everytime we start a viewer
    global current
    current = IntVar()
    current.set(0)
    current.trace("w", enableNav)
    global mediaLabel
    mediaLabel = None
    
    os.chdir(photoDir)
    
    global vName
    global vHandle
    global vFavCount
    global vRtCount 
    global vHasht 
    global vText

    vName = StringVar()
    vHandle = StringVar()
    vFavCount = StringVar()
    vRtCount = StringVar()
    vHasht = StringVar()
    vText = StringVar()
    vImage = StringVar() 

    vName.set(tweets[current.get()]['name'])
    vHandle.set(tweets[current.get()]['handle'])
    vFavCount.set(tweets[current.get()]['favCount'])
    vRtCount.set(tweets[current.get()]['rtCount'])
    vHasht.set(tweets[current.get()]['hashtags'])
    vText.set(tweets[current.get()]['text']) 
    
    if tweets[current.get()]['imgName']:
        if not os.path.exists(tweets[current.get()]['imgName']):
            print("Error. Photo supposedly exists but not found") 
        else:
            img = ImageTk.PhotoImage(Image.open(tweets[current.get()]['imgName']))
    else:
        img = None

    viewer = Toplevel(mainWindow)
    viewer.title("Tweet Viewer")
    viewer.lift(root)
    viewer.minsize(width=600, height=800)
    viewer.maxsize(width=600, height=800)
    viewer.grid_propagate(0)
    #############################################################################
    stats = ttk.Labelframe(viewer, text='Statistics')
    info = ttk.Labelframe(viewer, text='User Information')
    tweet = ttk.Labelframe(viewer, text="Tweet")
    media = ttk.Labelframe(viewer, text="Media")
    #################################################################################
    media.grid(column = 1, row = 0)
    info.grid(column = 1, row = 1)
    tweet.grid(column = 1, row = 2)
    stats.grid(column = 1, row = 3)
    ################################################################################
    mediaLabel = ttk.Label(media, text="No Image Available"
                            , image=img)
    mediaLabel.grid(column=0, row=0, sticky=(N,S,E,W))
    ################################################################################3
    ttk.Label(info, text="Display Name:").grid(column=0, row=0, sticky=W)
    ttk.Label(info, textvariable=vName).grid(column=1, row=0, sticky=W)
    ttk.Label(info, text="Handle:").grid(column=0, row=1, sticky=W)
    ttk.Label(info, textvariable=vHandle).grid(column=1, row=1, sticky=W)
    ############################################################################3
    ttk.Label(tweet, textvariable=vText, wraplength = 400).grid(column=0, row=0)
    ############################################################################
    ttk.Label(stats, text="Favorites:").grid(column=0, row=0, sticky=W)
    ttk.Label(stats, textvariable=vFavCount).grid(column=1, row=0, sticky=W)
    ttk.Label(stats, text="Retweets:").grid(column=2, row=0, sticky=E)
    ttk.Label(stats, textvariable=vRtCount).grid(column=3, row=0, sticky=E)
    ttk.Label(stats, text="Hashtags:").grid(column=0, row=1, sticky=W)
    ttk.Label(stats, textvariable=vHasht).grid(column=1, row=1, sticky=W)
    ############################################################################
    for child in viewer.winfo_children(): child.grid_configure(padx=5, pady=5)
    for child in stats.winfo_children(): child.grid_configure(padx=5, pady=5)
    for child in info.winfo_children(): child.grid_configure(padx=5, pady=5)
    ########################################################################333
    global nextButton
    global prevButton
    prevButton = ttk.Button(viewer, text="Previous", 
               command=prevTweet, state='disabled')
    prevButton.grid(column=0, row=2, sticky=W)

    nextButton = ttk.Button(viewer, text="Next", 
               command=nextTweet)
    nextButton.grid(column=2, row=2, sticky=W)
    
    viewer.mainloop()


def nextTweet():
    global current
    global vName
    global vHandle
    global vFavCount
    global vRtCount 
    global vHasht 
    global vText
    current.set(current.get()+1)

    vName.set(tweets[current.get()]['name'])
    vHandle.set(tweets[current.get()]['handle'])
    vFavCount.set(tweets[current.get()]['favCount'])
    vRtCount.set(tweets[current.get()]['rtCount'])
    vHasht.set(tweets[current.get()]['hashtags'])
    vText.set(tweets[current.get()]['text']) 
    if tweets[current.get()]['imgName']:
        if not os.path.exists(tweets[current.get()]['imgName']):
            print("Error. Photo supposedly exists but not found") 
        else:
            img = ImageTk.PhotoImage(Image.open(tweets[current.get()]['imgName']))
    else:
        img = None
    global mediaLabel
    mediaLabel.configure(image = img)
    mediaLabel.image = img

def prevTweet():
    global current
    global vName
    global vHandle
    global vFavCount
    global vRtCount 
    global vHasht 
    global vText
    current.set(current.get()-1)

    vName.set(tweets[current.get()]['name'])
    vHandle.set(tweets[current.get()]['handle'])
    vFavCount.set(tweets[current.get()]['favCount'])
    vRtCount.set(tweets[current.get()]['rtCount'])
    vHasht.set(tweets[current.get()]['hashtags'])
    vText.set(tweets[current.get()]['text']) 
    if tweets[current.get()]['imgName']:
        if not os.path.exists(tweets[current.get()]['imgName']):
            print("Error. Photo supposedly exists but not found") 
        else:
            img = ImageTk.PhotoImage(Image.open(tweets[current.get()]['imgName']))
    else:
        img = None
    global mediaLabel
    mediaLabel.configure(image = img)
    mediaLabel.image = img


def askdirectory():
    """Returns a selected directoryname."""
    wd = filedialog.askdirectory()
    workDir.set(wd)


##############################################################################3

# Set up root and main frame
root = Tk()
root.title("Creepy Twitter")

mainWindow = ttk.Frame(root, padding = "3 3 12 12")
mainWindow.grid(column=0, row=0, sticky=(N, W, E, S))
mainWindow.columnconfigure(0, weight=1)
mainWindow.rowconfigure(0, weight=1)

# Set up string variables for labels and data entry

query = StringVar() 
query.trace("w", enableButton)
lang = StringVar() 
nTweets = StringVar()
nFlush = StringVar()
media = StringVar()
mSize = StringVar()
viewMedia = StringVar()
saveMedia = StringVar()
workDir = StringVar()
saveLog = StringVar()
logName = StringVar()

# Set settings
defaultSettings()
#####################################################################################
# Building menus
root.option_add('*tearOff', FALSE)
menubar = Menu(root)
root['menu'] = menubar
menuFile = Menu(menubar)
menuEdit = Menu(menubar)
menubar.add_cascade(menu=menuFile, label='File')
menubar.add_cascade(menu=menuEdit, label='Edit')
#*************************************************************************************
menuFile.add_command(label='New')
menuFile.add_command(label='Open')
menuFile.add_command(label='Close')
#*************************************************************************************
contextMenu = Menu(root)
for i in ('One', 'Two', 'Three'):
    contextMenu.add_command(label=i)
if (root.tk.call('tk', 'windowingsystem')=='aqua'):
    root.bind('<2>', lambda e: contextMenu.post(e.x_root, e.y_root))
    root.bind('<Control-1>', lambda e: menu.post(e.x_root, e.y_root))
else:
    root.bind('<3>', lambda e: contextMenu.post(e.x_root, e.y_root))

######################################################################################
#Set up static labels next to entry fields
ttk.Label(mainWindow, text="Query").grid(column=1, row=1, sticky=E)
ttk.Label(mainWindow, text="Language").grid(column=1, row=2, sticky=E)
ttk.Label(mainWindow, text="# of Tweets").grid(column=1, row=4, sticky=E)
ttk.Label(mainWindow, text="Stream Size").grid(column=1, row=5, sticky=E)
ttk.Label(mainWindow, text="Contains Media").grid(column=1, row=6, sticky=E)
ttk.Label(mainWindow, text="View Media").grid(column=1, row=9, sticky=E)
ttk.Label(mainWindow, text="Media Size").grid(column=1, row=10, sticky=E)
ttk.Label(mainWindow, text="Save Media").grid(column=1, row=11, sticky=E)
ttk.Label(mainWindow, text="Output Directory").grid(column=1, row=12, sticky=E)
ttk.Label(mainWindow, text="Print Log").grid(column=1, row=13, sticky=E)
ttk.Label(mainWindow, text="Log Name").grid(column=1, row=14, sticky=E)

# Set up entry fields
######################################################################################3
query_entry = ttk.Entry(mainWindow, textvariable=query)
query_entry.grid(column=2, row=1, sticky=W)
#*************************************************************************************
langCombo = ttk.Combobox(mainWindow, textvariable=lang, 
                          values = ('-', 'en', 'ar', 'jp'))
langCombo.grid(column=2, row=2, sticky=W)
#*************************************************************************************
nTweets_entry = ttk.Entry(mainWindow, textvariable=nTweets)
nTweets_entry.grid(column=2, row=4, sticky=W)
#*************************************************************************************
nFlush_entry = ttk.Entry(mainWindow, textvariable=nFlush)
nFlush_entry.grid(column=2, row=5, sticky=W)
#*************************************************************************************
any_media_button = ttk.Radiobutton(mainWindow, text='Fetch all tweets',
                    variable=media, value='-')
yes_media_button = ttk.Radiobutton(mainWindow, text='Fetch only tweets with media',
                    variable=media, value='True')
no_media_button = ttk.Radiobutton(mainWindow, text='Fetch only tweets with media',
                    variable=media, value='False')

any_media_button.grid(column=2, row=6, sticky=W)
yes_media_button.grid(column=2, row=7, sticky=W)
no_media_button.grid(column=2, row=8, sticky=W)
#*************************************************************************************
viewMedia_check = ttk.Checkbutton(mainWindow, variable=viewMedia,
	    onvalue='True', offvalue='False',
            text = 'Check to view media without saving it',
            command=callbackViewMedia)
viewMedia_check.grid(column=2, row=9, sticky=W)
#*************************************************************************************
mSizeCombo = ttk.Combobox(mainWindow, textvariable=mSize, 
                          values = ('thumb', 'small', 'medium', 'large'),
                          state='readonly')

mSizeCombo.grid(column=2, row=10, sticky=W)

#*************************************************************************************
saveMediaCheck = ttk.Checkbutton(mainWindow, variable=saveMedia,
	    onvalue='True', offvalue='False', 
            text = 'Check to save media to drive',
            command = callbackSaveMedia)
saveMediaCheck.grid(column=2, row=11, sticky=W)
#*************************************************************************************
workDirEntry = ttk.Entry(mainWindow, textvariable=workDir, state='disabled')
workDirEntry.grid(column=2, row=12, sticky=W)
workDirButton = ttk.Button(mainWindow, text="select", 
           command=askdirectory, state='normal')
workDirButton.grid(column=3, row=12, sticky=W)
#*************************************************************************************
saveLogCheck = ttk.Checkbutton(mainWindow, variable=saveLog,
	    onvalue='True', offvalue='False', 
            text = 'Check to save log to drive',
            command = callbackLogEntry)
saveLogCheck.grid(column=2, row=13, sticky=W)
#*************************************************************************************
logNameEntry = ttk.Entry(mainWindow, textvariable=logName, state='normal')
logNameEntry.grid(column=2, row=14, sticky=W)
#*************************************************************************************
bar = ttk.Progressbar(mainWindow, orient=HORIZONTAL, length=200, mode='indeterminate')
bar.grid(column=2, row=15, sticky=W)
######################################################################################3
fetchButton = ttk.Button(mainWindow, text="Fetch", 
           command=fetch, state='disabled')
fetchButton.grid(column=3, row=15, sticky=W)
######################################################################################3
viewerButton = ttk.Button(mainWindow, text="Viewer", 
           command=initViewer, state='normal')
viewerButton.grid(column=3, row=16, sticky=W)

######################################################################################3
# Add padding for all children
for child in mainWindow.winfo_children(): child.grid_configure(padx=5, pady=5)

######################################################################################3
######################################################################################3
# Convenience stuff
query_entry.focus()
# root.bind('<Return>', fetch)

root.mainloop()

