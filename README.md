
## No-IP Autorenew GUI

# Table of Contents

1. [How it Works](#how-it-works)
2. [Required Pre-Setup](#required-pre-setup)
3. [Running the Application](#running-the-application)
4. [Building It Yourself](#building-it-yourself)

This project serves as a "wrapper" for the [No-IP renewal Docker script](https://github.com/simao-silva/noip-renewer). It allows you to renew one or multiple No-IP domains either manually or automatically using a catch-all email.

![demo](https://raw.githubusercontent.com/callbacked/noip-autorenew-gui/master/assets/demo.png)

## How it Works

![overview](https://raw.githubusercontent.com/callbacked/noip-autorenew-gui/2a86e95a41c3bbc5c76c3f01345116ad239c58cb/assets/overview.svg) 

1. **Email Forwarding:** Forward your No-IP domain emails to a catch-all email. The application monitors this inbox for renewal notices.

2. **Initial Setup:** Enter your catch-all email credentials in the application. 

   ![step1](https://raw.githubusercontent.com/callbacked/noip-autorenew-gui/master/assets/step1.gif)

3. **No-IP Login:** Enter your No-IP login details in the "Accounts with Domains" section. Make sure your login email is forwarded to the catch-all email.

   This setup is necessary to run the [No-IP renewal Docker script](https://github.com/simao-silva/noip-renewer): `docker run --rm -it simaofsilva/noip-renewer:latest <EMAIL> <PASSWORD>`

   ![step2](https://raw.githubusercontent.com/callbacked/noip-autorenew-gui/master/assets/step2.gif)

## Required Pre-Setup
NOTE: Currently only gmail catch-all emails work since that is what I used when I made this application. If I get around to supporting more email providers I will change it in the documentation. 

Before running the application, you need:

1. **A catch-all email (using gmail) with an [app password](https://myaccount.google.com/apppasswords), if app passwords are not available, [turn on 2FA](https://support.google.com/accounts/answer/185839) and try again**.
2. **Your No-IP account login credentials (whose email will be forwarded to the catchall)**

### Forwarding Emails

1. Configure your No-IP domain email accounts to forward emails with the following subjects **to your catch-all email:**
   - "ACTION REQUIRED" from @noip.com
   - "No-IP Verification Code" from @noip.com

   Here is an example of how I did it using gmail:
   
   *For instance, if I had an account with No-IP that was registered with user@gmail.com, I would log in to its gmail account and forward the emails like this*

![example](https://raw.githubusercontent.com/callbacked/noip-autorenew-gui/master/assets/gmailexample.png)
[*(For more information about forwarding emails on gmail)*](https://support.google.com/mail/answer/10957?hl=en)

2. Repeat for each No-IP domain email that you want to use for future renewals.

Note: this step takes quite a long time if you have a lot of domain emails you want to use, sadly there is not a better way to do this.

## Running the Application

1. Start the Docker container:

   `docker run --name noip-autorenew-gui -d -p 5011:5000 callbacked/noip-autorenew-gui:latest`

2. Open your browser and go to `localhost:5011`. 

3. Enter your catch-all email and No-IP login account(s) in the UI.

## Building It Yourself

1. Clone the repository:

   `git clone https://github.com/callbacked/noip-autorenew-gui && cd noip-autorenew-gui`

2. Build the Docker image:

   `docker build -t noip-autorenew-gui:latest .`

3. Run the Docker container:

   `docker run --name noip-autorenew-gui -d -p 5011:5000 noip-autorenew-gui:latest`
