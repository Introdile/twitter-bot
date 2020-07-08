# How to set up this twitter bot!

Buckle in, this is a lot if you've never done it before. We'll be using Heroku to run this bot for us, but you could run it from your computer or something else. That won't be covered here, however!

Step 0 is downloads! You'll need:

A) This bot! On the upper right, hit the Code button and then download the zip. Unzip it somewhere you can find it, like your desktop.   
B) Git! You can go here for that, if you don't already have it installed: https://git-scm.com/downloads  
C) Heroku CLI! Right here: https://devcenter.heroku.com/articles/heroku-cli

Go ahead and get those installed. Now...

1. Create a new twitter account! If you use gmail, you can add a . or a +1 to the end of you email so you don't have to make a new one. Unfortunately, you'll have to add a phone number to it.

2. WHILE SIGNED IN TO THE NEW ACCOUNT, go to [developer.twitter.com](https://developer.twitter.com/) and click "Apply" on the upper right. You're going to be applying for a developer account and it'll ask a few questions. You will have to do a bit of typing, make sure it's coherent and try your best to channel your inner highschooler and fluff it out to hit the 200/100 character limit on the forms. 

3. Once done, you'll get an email to verify! Click it to verify and it'll ask if you wanna make your app. Give it a name and copy the API key and API secret key and put them aside. Click "Skip to Dashboard", then on the dashboard click the key icon next to the project you named. At the bottom, click "Generate" for the Access Token & Secret. Copy those with your API key and API key secret (make sure to label them!) and put those aside. NEVER SHOW THESE KEYS TO ANYONE! They're pretty much the password to your bot's account!

By the way, what you name your app isn't important, but it will show up under all your bot's automated tweets.
![alt text](https://i.imgur.com/OGELIOn.png "Try not to give it an inappropriate name!")

4. Let's set up the bot for you before getting into Heroku. The bot's main script is called "main.py", find it in the bot's folder and open it in any text editor, like Notepad. Here are the okay-to-edit sections of the script:

![alt text](https://i.imgur.com/QTZa0vr.png "You can change things highlighted in yellow!")

The comments around each setting should explain what each item does! Keep any strings (like twitter @'s) in between apostrophes.  
**source_accounts** can have any number of accounts added, seperated by commas. You can even have 1 account, but be sure to keep it in the square brackets. Again, be sure to ask permission before adding accounts you don't own or control to this field.  
**replace_word** can only be one word and will replace any word within the exclude_words regex. These settings are optional, you don't have to touch either of them, if you like. (and sorry those two should be next to each other, I messed up lol)

**can_reply** tells whether your bot will always be running or not. **Here's an important note about this setting:** If you set it to true, you will have to give Heroku your credit card details. *They will not charge you*, but if you don't, your bot will be shut off probably around half-way through a month and won't come back on until the beginning of the next month. If you turn it off, you won't have to give Heroku your card details, but your bot will not be able to reply to anyone. You'll also have to set up an scheduler in Heroku that I'll go over later.

Go ahead and save the settings when you're all done. Don't touch anything else in the script if you don't know what you're doing! (TODO: seperate settings file)

5. Next we're gonna get set up on Heroku. Go ahead and make an account here: https://www.heroku.com/  
If you want the bot to be able to reply, *you have to enter your credit card details.* You can run one full-time twitter bot without accruing charges. Go to your Account Settings on Heroku, then to Billing, and add a card at the top. If you have any worries, [here's my past 8 months of invoices from running my own bot full-time.](https://i.imgur.com/tPm0RKj.png)

6. With your Heroku account set up, now we get to the fun stuff. Open Command Prompt (hit Win key + R and type CMD or find it in the start menu) and navigate to where you extracted this bot. If you extracted it to your desktop, you'll get to it with this command:

        cd desktop/twitter-bot
        
![alt text](https://i.imgur.com/qhOrdOP.png "It'll look like this, hopefully!")

You should be in the twitter-bot directory! Now type or copy and paste this command into command prompt to create a git repository:

       git init

Add all the files to that git with this command:

      git add .
      
Now commit it!

      git commit -a "Adding all these dang files"
      
Now with this next command, it'll use the Heroku CLI you installed to create and app for you. This will prompt you to log in, which you just hit a key to open your browser and press a button. This will link the CLI to your Heroku account.

      heroku create --stack cedar
      
We're almost done, so we're going to enter those keys we got earlier in step 3. We need the API key, API secret key, Access Token, and Access Secret Token. If you don't have those saved, you can go back up to your twitter developer account and generate a new set of keys. Copy and paste these commands into a text editor then replace the text after the equal (=) with the appropriate key for each of them. Paste into command prompt and it'll enter them sequentially for you.

    heroku config:set TWITTER_CONSUMER_KEY=your_api_key_here
    heroku config:set TWITTER_CONSUMER_SECRET=your_api_secret_key_here
    heroku config:set TWITTER_ACCESS_TOKEN_KEY=your_access_token_here
    heroku config:set TWITTER_ACCESS_SECRET=your_access_secret_token_here

![alt text](https://i.imgur.com/TFgSsZx.png "REMEMBER NOT TO SHOW YOUR KEYS TO ANYONE!")

Okay! With that all set up, here's the last couple of commands. This next one will push all your files to Heroku. *This may take a couple minutes as it sets everything up on their end*:

    git push heroku master
    
Now if you've set up your bot to reply, you can just type this and you're done!

    heroku run worker
    
...and you're golden! If you don't want your bot replying, here's how to set up a scheduler on Heroku so it won't be running all the time.

**TODO: HOW TO MAKE SCHEDULER**
