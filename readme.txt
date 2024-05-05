Summary: This application uses confluent kafka to create a team based trivia web game where users attempt to guess the answer to questions provided by admin. 

Detailed Description with API navigation:
Users are greeted with a login page which require them to login using one of the three precreated teams:
admin: password
TeamAlpaca: spitcamel
TeamStalactites: pointyrock
The login information is stored in a kafka topic and is read to check for valid logins. 
NOTE: Your login is stored in your cookies so if you want to change teams you will have to manually naviagte to the "/login" endpoint.
After logging in users will find a page of all the questions which have been asked since the zookeeper/broker image was created (not run, data persists between runs however I have added an admin ability to delete topics if they need to) Users can then select the question they would like to answer and will be linked to that question's chatroom. All the previous incorrect answers for that question will be shown in a chatbox which updates automatically. Users can use a textbox shown on screen to enter their guesses for the asnwer to the question. Once somebody guesses the right answer the server will send a message in the chat announcing the winner and locking the chat from future submissions. This is done by adding the topic to a list of completed topics that is checked before the server allows users to post into the question topic. There is also a button to return to the previous question selection screen.
When viewing the question selection screen users will notice a green Admin Dashboard button in the top right of the screen. If the user is logged in with admin credentials they can click the green Admin Dashboard button to be linked to the admin dashboard.
On the admin dashboard users can view Three additional screens:
Screen1-Admin create question: Where admins can add new questions for users to guess at using the textbox. There is a button to return to the admin dashboard
Screen2-Admin usage statistics: A screen that compiles usage statistics for the programs endpoints. This data is for the current worker processing the request so it will tell you session data if you run the program with only a single worker, or will give you feedback for the servicing one if theres multiple workers. 
NOTE: All usage data frome all workers since the zookeeper-broker were created is stored in the usagestatistics topic.
NOTE_2: There is commented out code to make this endpoint show the usage stats for all workers since broker creation but its non-functional at the moment.
NOTE_3: Theres no back button from this screen use the url line to manually route to a different screen or use the back button on your browser.
Screen3-Admin topics: A screen which contains all the topics which make up the entire program, from here admin can select a topic to view all the messages in said topic or they can choose to delete this topics.
WARNING: This list of topics includes server configurations and operation critical topics such as "users" exercise caution.
NOTE: The usagestatistics topic contains all usage data since the broker was created.
NOTE_3: Theres no back button from this screen use the url line to manually route to a different screen or use the back button on your browser.
There is a final button on the Admin Dashboard titled "Home" which allows the user to return to the question selection screen.

Instructions for installation:
1. Clone/Download the git repository into a linux based environment with python(I used WSL and python 3.12.1)
NOTE: The ContainerizedWIP.zip file contains the most recent development branch of the program which attempts to dockerize the app.py portion of the program and link everything together with compose.
2. Install Docker (with Compose)
3. I recommend setting up a virtual environment but it is possible to run without one. 
	Run: sudo apt install python3.11-venv
	Run: python3.12 -m venv venv
4. Run the following command to prep the environment: pip install -r requirements.txt
5. To begin the zookeeper and broker in the background run: docker-compose up -d
6. Run the following command where NUM_WORKERS is replaced with the number of gunicorn workers you would like to spin the instance up with: gunicorn -w NUM_WORKERS -b 127.0.0.1:5000 app:app --timeout 600
7. Open your browser and go to localhost:5000. You should now be using the app :)
