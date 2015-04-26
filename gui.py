from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from twitter2 import *
import time
import inspect
from PIL import Image, ImageTk
import os


def str2Bool(str):
    if str == "True":
        result = True
    else:
        result = False
    
    return result

class Fetcher(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        parent.title("Twitter Licker")

        # At first, there are no tweets and nothing
        self.fetched = BooleanVar()
        self.fetched.set(False) # This means we haven't fetched yet
        self.fetched.trace("w", self.enableViewerButton) # Disabled button until we fetch

        self.tweets = None
        self.photoDir = None
        self.total = None

        self.rootDir = os.getcwd()

        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.initUI()

    def initUI(self):
        
        # Set up string variables for labels and data entry
        self.query = StringVar() 
        self.query.trace("w", self.enableFetchButton)
        self.lang = StringVar() 
        self.nTweets = StringVar()
        self.nFlush = StringVar()
        self.media = StringVar()
        self.mSize = StringVar()
        self.viewMedia = StringVar()
        self.saveMedia = StringVar()
        self.workDir = StringVar()
        self.saveLog = StringVar()
        self.logName = StringVar()

        # Set settings
        self.defaultSettings()
        #####################################################################################
        # Set up Menus
        self.initMenuBar()
        self.initContextMenu()
        ######################################################################################
        #Set up static labels (tags for entry fields)
        ttk.Label(self, text="Query").grid(column=1, row=1, sticky=W)
        ttk.Label(self, text="Language").grid(column=1, row=2, sticky=W)
        ttk.Label(self, text="# of Tweets").grid(column=1, row=4, sticky=W)
        ttk.Label(self, text="Contains Media").grid(column=1, row=6, sticky=W)
        ttk.Label(self, text="View Media").grid(column=1, row=9, sticky=W)
        ttk.Label(self, text="Media Size").grid(column=1, row=10, sticky=W)
        ttk.Label(self, text="Save Media").grid(column=1, row=11, sticky=W)
        ttk.Label(self, text="Output Directory").grid(column=1, row=12, sticky=W)
        ttk.Label(self, text="Print Log").grid(column=1, row=13, sticky=W)
        ttk.Label(self, text="Log Name").grid(column=1, row=14, sticky=W)

        # Set up entry fields
        ######################################################################################3
        self.queryEntry = ttk.Entry(self, textvariable=self.query)
        self.queryEntry.grid(column=2, row=1, sticky=W)
        #*************************************************************************************
        self.langCombo = ttk.Combobox(self, textvariable=self.lang, 
                                  values = ('-', 'en', 'ar', 'jp'))
        self.langCombo.grid(column=2, row=2, sticky=W)
        #*************************************************************************************
        self.nTweetsEntry = ttk.Entry(self, textvariable=self.nTweets)
        self.nTweetsEntry.grid(column=2, row=4, sticky=W)
        #*************************************************************************************
        self.anyMediaButton = ttk.Radiobutton(self, text='Fetch all tweets',
                            variable=self.media, value='-')
        self.yesMediaButton = ttk.Radiobutton(self, text='Fetch only tweets with media',
                            variable=self.media, value='True')
        self.noMediaButton = ttk.Radiobutton(self, text='Fetch only tweets without media',
                            variable=self.media, value='False')

        self.anyMediaButton.grid(column=2, row=6, sticky=W)
        self.yesMediaButton.grid(column=2, row=7, sticky=W)
        self.noMediaButton.grid(column=2, row=8, sticky=W)
        #*************************************************************************************
        self.viewMediaCheck = ttk.Checkbutton(self, variable=self.viewMedia,
                    onvalue='True', offvalue='False',
                    text = 'Check to view media without saving it',
                    command=self.callbackViewMedia)
        self.viewMediaCheck.grid(column=2, row=9, sticky=W)
        #*************************************************************************************
        mSizeValues = ('thumb', 'small', 'medium', 'large')
        self.mSizeCombo = ttk.Combobox(self, textvariable=self.mSize, 
                                  values = mSizeValues, state='readonly')
        self.mSizeCombo.grid(column=2, row=10, sticky=W)
        #*************************************************************************************
        self.saveMediaCheck = ttk.Checkbutton(self, variable=self.saveMedia,
                    onvalue='True', offvalue='False', 
                    text = 'Check to save media to drive',
                    command = self.callbackSaveMedia)
        self.saveMediaCheck.grid(column=2, row=11, sticky=W)
        #*************************************************************************************
        self.workDirEntry = ttk.Entry(self, textvariable=self.workDir, state='disabled')
        self.workDirEntry.grid(column=2, row=12, sticky=W)
        
        self.workDirButton = ttk.Button(self, text="select", 
                   command=self.askDirectory, state='disabled')
        self.workDirButton.grid(column=3, row=12, sticky=W)
        #*************************************************************************************
        self.saveLogCheck = ttk.Checkbutton(self, variable=self.saveLog,
                    onvalue='True', offvalue='False', 
                    text = 'Check to save log to drive',
                    command = self.callbackLogEntry)
        self.saveLogCheck.grid(column=2, row=13, sticky=W)
        #*************************************************************************************
        self.logNameEntry = ttk.Entry(self, textvariable=self.logName, state='normal')
        self.logNameEntry.grid(column=2, row=14, sticky=W)
        #*************************************************************************************
        #bar = ttk.Progressbar(mainWindow, orient=HORIZONTAL, length=200, mode='indeterminate')
        #bar.grid(column=2, row=15, sticky=W)
        ######################################################################################3
        self.fetchButton = ttk.Button(self, text="Fetch", command=self.fetch, 
                                        state='disabled')
        self.fetchButton.grid(column=3, row=15, sticky=W)
        ######################################################################################3
        self.viewerButton = ttk.Button(self, text="Viewer", 
                   command=self.initViewer, state='disabled')
        self.viewerButton.grid(column=3, row=16, sticky=W)

        ######################################################################################3
        # Add padding for all children
        for child in self.winfo_children(): child.grid_configure(padx=5, pady=5)
        
        self.queryEntry.focus()
        self.parent.bind('<Return>', self.fetch)

    def initMenuBar(self):
        # Building menus
        self.parent.option_add('*tearOff', FALSE)
        self.menubar = Menu(root)
        self.parent['menu'] = self.menubar
        self.menuFile = Menu(self.menubar)
        self.menuEdit = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menuFile, label='File')
        self.menubar.add_cascade(menu=self.menuEdit, label='Edit')
        #*************************************************************************************
        self.menuFile.add_command(label='New')
        self.menuFile.add_command(label='Open')
        self.menuFile.add_command(label='Close')
        #*************************************************************************************
        self.menuEdit.add_command(label='Authentication Settings', command=self.initAuth)
        self.menuEdit.add_command(label='Preferences', command=self.initPref)

    def initContextMenu(self):
        self.contextMenu = Menu(self.parent)
        for i in ('One', 'Two', 'Three'):
            self.contextMenu.add_command(label=i)
        if (self.parent.tk.call('tk', 'windowingsystem')=='aqua'):
            self.parent.bind('<2>', lambda e: self.contextMenu.post(e.x_root, e.y_root))
            self.parent.bind('<Control-1>', lambda e: self.contextMenu.post(e.x_root, e.y_root))
        else:
            self.parent.bind('<3>', lambda e: self.contextMenu.post(e.x_root, e.y_root))

    def getDefaultArgs(self, func):
        args, varargs, keywords, defaults = inspect.getargspec(func)
        return dict(zip(args[-len(defaults):], defaults))

    def defaultSettings(self):
        defaultArgs = self.getDefaultArgs(fetch_tweets)
        self.lang.set(defaultArgs['lang'])
        self.nTweets.set(defaultArgs['nTweets'])
        self.nFlush.set(defaultArgs['nFlush'])
        self.media.set(defaultArgs['media'])
        self.mSize.set(defaultArgs['mSize'])
        self.viewMedia.set(defaultArgs['viewMedia'])
        self.saveMedia.set(defaultArgs['saveMedia'])
        self.workDir.set(defaultArgs['workDir'])
        self.saveLog.set(defaultArgs['saveLog'])
        self.logName.set(defaultArgs['logName'])

        self.credentials = {}
        with open("authSettings.txt", 'r') as f:
            for line in f:
                items = line.split()
                (key, values) = (items[0], items[1])
                self.credentials[key] = values

    def enableFetchButton(self, *args):
        if self.query.get():
            self.fetchButton.configure(state='normal')
        else:
            self.fetchButton.configure(state='disabled')

    def enableViewerButton(self, *args):
        if self.fetched.get():
            self.viewerButton.configure(state='normal')
        else:
            self.viewerButton.configure(state='disabled')

    def callbackViewMedia(self, *args):
        if self.viewMedia.get() == "True":
            self.mSizeCombo.configure(state="readonly")
        else:
            self.mSizeCombo.configure(state="disabled")

    def callbackSaveMedia(self, *args):
        if self.saveMedia.get() == "True":
            self.workDirEntry.configure(state="normal")
            self.workDirButton.configure(state='normal') 
            self.workDir.set(time.strftime("%d_%b_%Y_%H.%M.%S"))
        else:
            self.workDirEntry.configure(state="disabled")
            self.workDirButton.configure(state='disabled') 
            self.workDir.set("cache")

    def callbackLogEntry(self, *args):
        if self.saveLog.get() == "True":
            self.logNameEntry.configure(state="normal")
        else:
            self.logNameEntry.configure(state="disabled")

    def askDirectory(self):
        """Returns a selected directoryname."""
        wd = filedialog.askdirectory()
        self.workDir.set(wd)

    def fetch(self, *args):
        try:
            #bar.start()
            query_ = self.query.get()
            if not query_:
                print("Returning due to empty query")
                return

            lang_ = self.lang.get()
            nTweets_ = int(self.nTweets.get())
            nFlush_ = int(self.nFlush.get())
            media_ = str2Bool(self.media.get())
            mSize_ = self.mSize.get()
            saveMedia_ = str2Bool(self.saveMedia.get())
            viewMedia_ = str2Bool(self.viewMedia.get())
            workDir_ = self.workDir.get()
            saveLog_ = str2Bool(self.saveLog.get())
            logName_ = self.logName.get()

            apiKey = self.credentials['apiKey']
            apiSecret = self.credentials['apiSecret']
            accessToken = self.credentials['accessToken']
            accessTokenSecret = self.credentials['accessTokenSecret']
            # Actually fetch the self.parent.tweets
            result = fetch_tweets(apiKey, apiSecret, accessToken, accessTokenSecret,
                                    query_, lang_, nTweets_, nFlush_, media_, 
                                  mSize_, saveMedia_, viewMedia_, workDir_,
                                  saveLog_, logName_)
            #bar.stop()
            self.tweets = result[0]
            self.total = result[1]
            self.photoDir = result[2]
            self.fetched.set(True)
            
            # Change back to original directory
            os.chdir(self.rootDir)

        except ValueError:
            pass

    def initViewer(self, *args):
        viewer = Viewer(self)
        viewer.mainloop()

    def initPref(self, *args):
        preferences = Preferences(self)
        preferences.mainloop()

    def initAuth(self, *args):
        authSettings = AuthSettings(self)
        authSettings.mainloop()

class Preferences(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self)
        self.parent = parent
        self.title("Preferences")
        self.lift(self.parent)

        self.initUI()

    def initUI(self):
        self.nFlush = StringVar()
        self.nFlush.set(self.parent.nFlush.get())

        # Set them to current settings
        ttk.Label(self, text="Stream Size: ").grid(column=0, row=0, sticky=W)
        ########################################################################333
        self.nFlushEntry = ttk.Entry(self, textvariable=self.nFlush)
        self.nFlushEntry.grid(column=1, row=0, sticky=W)
        ########################################################################333
        self.okButton = ttk.Button(self, text="OK", command=self.save)
        self.okButton.grid(column=1, row=1, sticky=E)

        self.resetButton = ttk.Button(self, text="Reset", command=self.reset)
        self.resetButton.grid(column=2, row=1, sticky=E)
        
        self.cancelButton = ttk.Button(self, text="Cancel", command=self.destroy)
        self.cancelButton.grid(column=3, row=1, sticky=E)
        ########################################################################333
        for child in self.winfo_children(): child.grid_configure(padx=5, pady=5)
        ########################################################################333
        self.nFlushEntry.focus()
        self.bind('<Return>', self.save)

    def reset(self):
        #self.credentials = {}
        #with open("defPreferences.txt", 'r') as f:
        #    for line in f:
        #        items = line.split()
        #        (key, values) = (items[0], items[1])
        #        self.credentials[key] = values
        self.nFlush.set(self.parent.nFlush.get())

    def save(self, *args):
        self.parent.nFlush.set(self.nFlush.get())
        #with open("authSettings.txt", 'w') as f:
        #    for key in self.parent.credentials.keys():
        #        item = self.parent.credentials[key]
        #        f.write(key)
        #        f.write("    ")
        #        f.write(item)
        #        f.write("\n")
        self.destroy()

class AuthSettings(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self)
        self.parent = parent
        self.title("Authentication Settings")
        self.lift(self.parent)

        self.initUI()

    def initUI(self):
        self.apiKey = StringVar()
        self.apiSecret = StringVar()
        self.accessToken = StringVar()
        self.accessTokenSecret = StringVar()
        
        self.apiKey.set(self.parent.credentials['apiKey'])
        self.apiSecret.set(self.parent.credentials['apiSecret'])
        self.accessToken.set(self.parent.credentials['accessToken'])
        self.accessTokenSecret.set(self.parent.credentials['accessTokenSecret'])

        # Set them to current settings
        ttk.Label(self, text="API Key: ").grid(column=0, row=0, sticky=W)
        ttk.Label(self, text="API Secret: ").grid(column=0, row=1, sticky=W)
        ttk.Label(self, text="Access Token: ").grid(column=0, row=2, sticky=W)
        ttk.Label(self, text="Access Token Secret: ").grid(column=0, row=3, sticky=W)
        ########################################################################333
        self.apiKeyEntry = ttk.Entry(self, textvariable=self.apiKey)
        self.apiKeyEntry.grid(column=1, row=0, sticky=W)
        self.apiSecretEntry = ttk.Entry(self, textvariable=self.apiSecret)
        self.apiSecretEntry.grid(column=1, row=1, sticky=W)
        self.accessTokenEntry = ttk.Entry(self, textvariable=self.accessToken)
        self.accessTokenEntry.grid(column=1, row=2, sticky=W)
        self.accessTokenSecretEntry = ttk.Entry(self, textvariable=self.accessTokenSecret)
        self.accessTokenSecretEntry.grid(column=1, row=3, sticky=W)
        ########################################################################333

        self.okButton = ttk.Button(self, text="OK", command=self.save)
        self.okButton.grid(column=1, row=6, sticky=E)

        self.resetButton = ttk.Button(self, text="Reset", command=self.reset)
        self.resetButton.grid(column=2, row=6, sticky=E)
        
        self.cancelButton = ttk.Button(self, text="Cancel", command=self.destroy)
        self.cancelButton.grid(column=3, row=6, sticky=E)
        ########################################################################333
        for child in self.winfo_children(): child.grid_configure(padx=5, pady=5)
        ########################################################################333
        self.apiKeyEntry.focus()
        self.bind('<Return>', self.save)
        
    def reset(self):
        self.credentials = {}
        with open("defAuthSettings.txt", 'r') as f:
            for line in f:
                items = line.split()
                (key, values) = (items[0], items[1])
                self.credentials[key] = values
        self.apiKey.set(self.credentials['apiKey'])
        self.apiSecret.set(self.credentials['apiSecret'])
        self.accessToken.set(self.credentials['accessToken'])
        self.accessTokenSecret.set(self.credentials['accessTokenSecret'])

    def save(self, *args):
        self.parent.credentials['apiKey'] = self.apiKey.get()
        self.parent.credentials['apiSecret'] = self.apiSecret.get()
        self.parent.credentials['accessToken'] = self.accessToken.get()
        self.parent.credentials['accessTokenSecret'] = self.accessTokenSecret.get()
        with open("authSettings.txt", 'w') as f:
            for key in self.parent.credentials.keys():
                item = self.parent.credentials[key]
                f.write(key)
                f.write("    ")
                f.write(item)
                f.write("\n")
        self.destroy()

class Viewer(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self)
        self.parent = parent
        self.title("Tweet Viewer")
        self.lift(self.parent)

        self.minsize(800, 800)
        self.maxsize(800, 800)
        
        self.initUI()

    def initUI(self):
        self.current = IntVar()
        self.current.set(0)
        self.current.trace("w", self.enableNav)
        
        os.chdir(self.parent.photoDir)
        
        self.name = StringVar()
        self.handle = StringVar()
        self.favCount = StringVar()
        self.rtCount = StringVar()
        self.hasht = StringVar()
        self.text = StringVar()
        self.image = StringVar() 

        self.name.set(self.parent.tweets[self.current.get()]['name'])
        self.handle.set(self.parent.tweets[self.current.get()]['handle'])
        self.favCount.set(self.parent.tweets[self.current.get()]['favCount'])
        self.rtCount.set(self.parent.tweets[self.current.get()]['rtCount'])
        self.hasht.set(self.parent.tweets[self.current.get()]['hashtags'])
        self.text.set(self.parent.tweets[self.current.get()]['text']) 
        
        if self.parent.tweets[self.current.get()]['imgName']:
            if not os.path.exists(self.parent.tweets[self.current.get()]['imgName']):
                print("Error. Photo supposedly exists but not found") 
            else:
                self.img = ImageTk.PhotoImage(Image.open(
                                self.parent.tweets[self.current.get()]['imgName']))
        else:
            self.img = None

        #############################################################################
        stats = ttk.Labelframe(self, text='Statistics')
        info = ttk.Labelframe(self, text='User Information')
        tweet = ttk.Labelframe(self, text="Tweet")
        media = ttk.Labelframe(self, text="Media")
        #################################################################################
        media.grid(column = 1, row = 0)
        info.grid(column = 1, row = 1)
        tweet.grid(column = 1, row = 2)
        stats.grid(column = 1, row = 3)
        self.grid_propagate(False)
        ################################################################################
        self.mediaLabel = ttk.Label(media, text="No Image Available"
                                , image=self.img)
        self.mediaLabel.grid(column=0, row=0, sticky=(N,S,E,W))
        ################################################################################3
        ttk.Label(info, text="Display Name: ").grid(column=0, row=0, sticky=W)
        ttk.Label(info, textvariable=self.name).grid(column=1, row=0, sticky=W)
        ttk.Label(info, text="Handle: ").grid(column=0, row=1, sticky=W)
        ttk.Label(info, textvariable=self.handle).grid(column=1, row=1, sticky=W)
        ############################################################################3
        ttk.Label(tweet, textvariable=self.text, wraplength = 400).grid(column=0, row=0)
        ############################################################################
        ttk.Label(stats, text="Favorites: ").grid(column=0, row=0, sticky=W)
        ttk.Label(stats, textvariable=self.favCount).grid(column=1, row=0, sticky=W)
        ttk.Label(stats, text="Retweets: ").grid(column=2, row=0, sticky=E)
        ttk.Label(stats, textvariable=self.rtCount).grid(column=3, row=0, sticky=E)
        ttk.Label(stats, text="Hashtags: ").grid(column=0, row=1, sticky=W)
        ttk.Label(stats, textvariable=self.hasht, wraplength=400).grid(column=1, row=1, sticky=W)
        ########################################################################333
        self.prevButton = ttk.Button(self, text="Previous", 
                   command=self.prevTweet, state='disabled')
        self.prevButton.grid(column=0, row=2, sticky=W)

        self.nextButton = ttk.Button(self, text="Next", 
                   command=self.nextTweet)
        self.nextButton.grid(column=2, row=2, sticky=W)
        ############################################################################
        for child in self.winfo_children(): child.grid_configure(padx=5, pady=5)
        for child in stats.winfo_children(): child.grid_configure(padx=5, pady=5)
        for child in info.winfo_children(): child.grid_configure(padx=5, pady=5)
        self.bind('<Left>', self.prevTweet)
        self.bind('<Right>', self.nextTweet)

    def enableNav(self, *args):
        if self.current.get() <= 0:
            self.prevButton.configure(state='disabled')
        elif self.current.get() >= self.parent.total-1:
            self.nextButton.configure(state='disabled')
        else:
            self.nextButton.configure(state='enabled')
            self.prevButton.configure(state='enabled')

    def nextTweet(self, *args):

        if self.current.get() >= self.parent.total-1:
            return

        self.current.set(self.current.get()+1)

        self.name.set(self.parent.tweets[self.current.get()]['name'])
        self.handle.set(self.parent.tweets[self.current.get()]['handle'])
        self.favCount.set(self.parent.tweets[self.current.get()]['favCount'])
        self.rtCount.set(self.parent.tweets[self.current.get()]['rtCount'])
        self.hasht.set(self.parent.tweets[self.current.get()]['hashtags'])
        self.text.set(self.parent.tweets[self.current.get()]['text']) 
        if self.parent.tweets[self.current.get()]['imgName']:
            if not os.path.exists(self.parent.tweets[self.current.get()]['imgName']):
                print("Error. Photo supposedly exists but not found") 
            else:
                self.img = ImageTk.PhotoImage(Image.open(self.parent.tweets[self.current.get()]['imgName']))
        else:
            self.img = None
        
        self.mediaLabel.configure(image = self.img)

    def prevTweet(self, *args):

        if self.current.get() <= 0:
            return

        self.current.set(self.current.get()-1)

        self.name.set(self.parent.tweets[self.current.get()]['name'])
        self.handle.set(self.parent.tweets[self.current.get()]['handle'])
        self.favCount.set(self.parent.tweets[self.current.get()]['favCount'])
        self.rtCount.set(self.parent.tweets[self.current.get()]['rtCount'])
        self.hasht.set(self.parent.tweets[self.current.get()]['hashtags'])
        self.text.set(self.parent.tweets[self.current.get()]['text']) 
        if self.parent.tweets[self.current.get()]['imgName']:
            if not os.path.exists(self.parent.tweets[self.current.get()]['imgName']):
                print("Error. Photo supposedly exists but not found") 
            else:
                self.img = ImageTk.PhotoImage(Image.open(self.parent.tweets[self.current.get()]['imgName']))
        else:
            self.img = None
        
        self.mediaLabel.configure(image = self.img)
##############################################################################3

root = Tk()
main = Fetcher(root)

root.mainloop()

