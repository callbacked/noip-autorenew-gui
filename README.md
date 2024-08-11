##  No-IP Autorenew GUI

This is project serves as a "wrapper" for the [No-IP renewal Docker script](https://github.com/simao-silva/noip-renewer). My goal was to expand upon its usage into something that can renew one or multiple No-IP domains you may have either manually **or automatically through the use of a catch-all email.**

![demo](https://raw.githubusercontent.com/callbacked/noip-autorenew-gui/master/assets/demo.png)

  
  

##  How it works

![overview](https://raw.githubusercontent.com/callbacked/noip-autorenew-gui/2a86e95a41c3bbc5c76c3f01345116ad239c58cb/assets/overview.svg)Before running, the user forwards their emails with accounts made with No-IP to a catch all email. **This is important as the program monitors the catch all email's inbox for renewal notices for ALL forwarded domain emails**

  

Starting out, the user puts in their catchall email's credentials in the application (by default an example is shown to new users).

  

![step1](https://raw.githubusercontent.com/callbacked/noip-autorenew-gui/master/assets/step1.gif)

  
  

Then, the user puts in their **No-IP login details** in "Accounts with Domains", **ensuring that the email for the login is already forwarded with the associated catch all.**

  

This is required for when the program is prompted to execute the [No-IP renewal Docker script](https://github.com/simao-silva/noip-renewer): ``docker run --rm -it simaofsilva/noip-renewer:latest <EMAIL> <PASSWORD>``

  
  

![step2](https://raw.githubusercontent.com/callbacked/noip-autorenew-gui/master/assets/step2.gif)
## Running

1.  ``docker run --name noip-autorenew-gui -d -p 5011:5000 callbacked/noip-autorenew-gui:latest``

2. Access the interface through ``localhost:5011``and add in your catch all email + domain emails in the GUI

3. Add in your catch-all email in the UI + your no-ip login account(s) 

## Building it yourself

1.  ``git clone https://github.com/callbacked/noip-autorenew-gui && cd noip-autorenew-gui``

2. ``docker build -t noip-autorenew-gui:latest .``

3. ``docker run --name noip-autorenew-gui -d -p 5011:5000 noip-autorenew-gui:latest``





