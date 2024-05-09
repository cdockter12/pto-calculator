<h3 align="center">PTO Tracker</h3>
<div>
  <p align="center">
    An app that automatically tracks your PTO, so you don't have to!
</p>
</div>

<!-- ABOUT THE PROJECT -->
## About The Project
This project was built to track your PTO as an additional check for companies that manually track hours. Now you can be
sure your PTO balance lines up with what is posted on your pay stub.

The app will update your PTO balance on the last day of the month at a rate of 3wks/yr if you're a junior employee, or
4wk/yr for senior employees.


<!-- GETTING STARTED -->
## Getting Started

For simplicity, this project utilizes a docker container. If you'd like to run locally in an environment instead,
instructions for that are listed below.

### Installation

1. Clone the Repo
   ```sh
   git clone https://github.com/cdockter12/pto-calculator.git
   ```
### Setup Homebrew, PostgreSQL
2. Confirm you have an updated version of [Homebrew](http://brew.sh/) installed. Then, use Homebrew to install Postgres (if not already installed):
   ```sh
	  brew install postgresql  
	  brew services start postgresql  
   ```
3. Create a postgres DB called pto-tracker, and a user/role with SUPERUSER and LOGIN rights.
   ```sh
      https://www.postgresql.org/docs/current/sql-createdatabase.html
      https://www.postgresql.org/docs/current/sql-createrole.html
      https://stackoverflow.com/questions/10757431/postgres-upgrade-a-user-to-be-a-superuser
   ```
4. Create a .env file in your project directory, and fill the following details regarding your new local database.
   ```sh
      DB_NAME_DEV=pto-tracker
      DB_USER_DEV=<your-name-from-above>
      DB_PASS_DEV=<your-pass-from-above>
      DB_HOST_DEV=localhost
      DB_PORT_DEV=5432
      ENV=development
      SECRET_KEY=<your-app-secret-key-here>
      MAIL_USERNAME=<your-email-address-you-want-notifications-from>
      MAIL_PASSWORD=<password-to-email-above>
   ```
5. Now we're ready to run this via python environment, or via the docker image & container.
#### Option 1 - Docker:
1. Install Docker
2. Build Image
   ```shell
   docker build -t pto-calculator .
   ```
3. Run container from image.
   ```shell
   docker run -e DB_HOST_DEV=docker.for.mac.host.internal --env-file .env -d -p 5000:5000 pto-calculator
   ```
   

#### Option 2 - Docker-less:
1. Setup virtual environment
   Make sure you have an updated version of [pyenv](https://github.com/pyenv/pyenv-installer) installed. Note, the new macOS (M1 chips & newer) uses the zsh profile instead of the bash profile.  If that is the case, replace "/.bash_profile" with "/.zsh_profile":
    ```
	  brew install pyenv  
	  brew install pyenv-virtualenv
      source ~/.bash_profile  
	```
   Use pyenv to install python 3.10:
   ```
	  pyenv install 3.10 
   ```

2. Create the application python environment. I called mine pto (due to the original scope of the project):
   ```
   cd ~/src/pto-calculator (or wherever you downloaded repo)  
   pyenv virtualenv 3.10 pto  
   pyenv local pto  
   ```
3. Install Python Packages.
   ``` 
	  pip install -r requirements.txt  
   ```
4. Run the app with: 
   ```
      flask run
   ```

<!-- USAGE EXAMPLES -->
## Usage

1. Register with current PTO balance.
2. Login
3. Adjust PTO when you take time off.
4. That's it!


![](https://media.giphy.com/media/l1Ku7Ru3ZzSRCd2zC/giphy.gif)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



