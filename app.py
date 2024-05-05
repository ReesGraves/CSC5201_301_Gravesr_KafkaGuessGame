from flask import Flask, request, render_template, redirect, url_for, Response, session, flash
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer, Producer, KafkaError, TopicPartition
import threading
import json
import uuid
import re

app = Flask(__name__)
app.secret_key = "TheSuperSecretKeyOfSecrecy_WhyAreYouLookingAtThis"
### Begin Kafka Functions
def sanitize_topic_name(topic: str):
    # Truncate the topic name to the first 250 characters
    # We will not be broken by someone inputting a 10k long
    # string to lag the server
    topic = topic[:250]
    # Replace spaces with underscores
    topic = topic.replace(" ", "_")
    
    # Convert to lowercase
    topic = topic.lower()
    
    # Remove all characters that arent valid Kafka topic characters
    # Valid characters are ASCII alphanumerica, '.', '-', and '_'
    # This regex finds any invalid characters and replaces them wit
    # an empty string, effectively removing it.
    topic = re.sub(r'[^a-z0-9._-]', '', topic)

    # Ensure the topic does not start with an underscore or a period
    while topic.startswith('_') or topic.startswith('.'):
        topic = topic[1:]
    # Check if the topic name is empty after sanitization
    if not topic:
        # Assign a default value if the topic name is empty
        topic = "TriedtoAddInvalidtopic"
    return topic

def kafka_message_generator(topic: str, username: str):
    consumer = create_consumer(topic, username)
    while True:
        message = consumer.poll(timeout=1.0)
        if message is None:
            continue
        if message.error():
            print("Consumer error: {}".format(message.error()))
            continue
        yield "data: {}\n\n".format(message.value().decode('utf-8'))

def admin_kafka_message_generator(topic: str, username: str):
    consumer = create_consumer(topic, username)
    while True:
        message = consumer.poll(timeout=1.0)
        if message is None:
            continue
        if message.error():
            print("Consumer error: {}".format(message.error()))
            continue
        if message.key():
            yield "data: {}\n\n".format({
        "key": message.key().decode('utf-8'),
        "value": message.value().decode('utf-8')
            })
        else:
            yield "data: {}\n\n".format({
        "value": message.value().decode('utf-8')
            })

def create_consumer(topic: str, username:str):
    topic = sanitize_topic_name(topic)
    group_id = str(uuid.uuid4())
    if topic == "users":
        consumer_id = "JohnDoe"
    else:
        consumer_id = str(username)
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': group_id,
        'client.id': consumer_id,
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe([topic])
    # Fetch all messages from the beginning
    partitions = consumer.assignment()
    for partition in partitions:
        consumer.assign([partition])
        consumer.seek(partition, 0)
    return consumer

def create_producer(client_id: str):
    configp = {
        'bootstrap.servers': 'localhost:9092',
        'client.id': str(client_id)
    }
    producer = Producer(configp)
    return producer

def is_topic_empty(topic: str):
    admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})
    
    try:
        # Get the list of topics
        topics_metadata = admin_client.list_topics(timeout=10)
        # If the topic don't exist it is empty
        if topic not in topics_metadata.topics:
            # print(f"Topic '{topic}' does not exist.")
            return True
        # if topic exist it is not empty
        else:
            return False
        
    # except Exception as e:
    #     print(f"Error while checking topic '{topic}': {e}")
    #     return True
    
    finally:
        # admin client closes itself
        pass


    # ###### Attempt 2 using .assignment ######
    # consumer = create_consumer(topic, "checker")
    # ### Since a topic cannot exist without entries we can just check if the
    # ### topic exist by checking if the consumer has any assignments
    # if not consumer.assignment():
    #     consumer.close()
    #     return True
    # # Consume one message to check if the topic is empty
    # try:
    #     message = None
    #     while message is None:
    #         message = consumer.poll(timeout=1.0)
    #         if message is None:
    #             # If no message is received, check if the consumer has reached the end of the topic
    #             # by checking if it is currently assigned partitions and those partitions are empty
    #             if consumer.assignment() and consumer.assignment().is_empty():
    #                 break  # No more messages in the topic, so break the loop
    #             continue
    #         if message.error():
    #             print("Consumer error: {}".format(message.error()))
    #             continue
                
    # finally:
    #     consumer.close()
    # return message is None
    ###### Attempt 1 #######
    ### Old way to check if topic is empty
    # # Consume one message to check if the topic is empty
    # try:
    #     message = None
    #     while message is None:
    #         message = consumer.poll(timeout=1.0)
    #         if message is None:
    #             # If no message is received, check if the consumer has reached the end of the topic
    #             # by checking if it is currently assigned partitions and those partitions are empty
    #             if consumer.assignment() and consumer.assignment().is_empty():
    #                 break  # No more messages in the topic, so break the loop
    #             continue
    #         if message.error():
    #             print("Consumer error: {}".format(message.error()))
    #             continue
                
    # finally:
    #     consumer.close()
    # # return message.value().decode('utf-8') 
    # return message is None

def Initiazlize_Topic(topic): 
    if topic == "questions":
        # return "Does this do something"
        boolfoo = is_topic_empty(topic)
        
        # If topic empty = True, create topic
        if boolfoo:
            # return("boolfoo="+str(boolfoo)+"ShouldOnlyseeIfTrue")
            # return "topic is empty"

            question = "name the best color"
            answer = "green"
            admin_produce_message_to_topic(topic=topic, message=question, answer=answer)
        else:
            # return("boolfoo="+str(boolfoo)+"ShouldOnlyseeIfFalse")
            pass
    elif topic == "users":
        # return "Does this do something"
        boolfoo = is_topic_empty(topic)
        
        # If users empty = True, create users topic with admin
        if boolfoo:
            ### Initialize all the users
            # Admin First
            configp = {
                    'bootstrap.servers': 'localhost:9092',
                    'client.id': 'GameInitializationProducer'
                }
            producer = Producer(configp)
            # Password
            messageOut_Value = "password"
            # Username
            key = "admin"
            topic = "users"
            producer.produce(topic=topic, value = messageOut_Value, key = str(key))
            # producer.flush()

            # Make Team one
            # Password
            messageOut_Value = "spitcamel"
            # Username
            key = "TeamAlpaca"
            topic = "users"
            producer.produce(topic=topic, value=messageOut_Value, key=str(key))
            # producer.flush()

            # Make Team two 
            # Password
            messageOut_Value = "pointyrock"
            # Username
            key = "TeamStalactites"
            topic = "users"
            producer.produce(topic=topic, value=messageOut_Value, key=str(key))
            producer.flush()
        # Else users already exist
        else:
            # return("boolfoo="+str(boolfoo)+"ShouldOnlyseeIfFalse")
            pass
    elif topic =="questions_completed":
        boolfoo = is_topic_empty(topic)
        # If users empty = True, create users topic with admin
        if boolfoo:
            ### Initialize "questions_completed"
            configp = {
                    'bootstrap.servers': 'localhost:9092',
                    'client.id': 'GameInitializationProducer'
                }
            producer = Producer(configp)
            topic = "questions_completed"
            value = "the_value_would_be_the_question_topic_name"
            key = "This could be the username of who solved it"
            producer.produce(topic=topic, value=value, key=key)
            producer.flush()
        else:
            pass
    # Else we dont know what we're initializing
    else:
        return "Unknown Initialization"

def list_topics():
    conf = {'bootstrap.servers': 'localhost:9092'}
    admin_client = AdminClient(conf)
    topics = admin_client.list_topics(timeout=10).topics
    # topics = admin_client.list_topics(timeout=10).topics.keys()  # Modify this line
    return topics
   
### Begin general Functions
def get_user_password(username: str, sender: str):
    consumer = create_consumer("users", sender)
    try:
        latest_password = None
        while latest_password is None:
            message = consumer.poll(timeout=1.0)
            if message is None:
                # If no message is received, check if the consumer has reached the end of the topic
                # by checking if it is currently assigned partitions and those partitions are empty
                if consumer.assignment() and consumer.assignment().is_empty():
                    break  # No more messages in the topic, so break the loop
                continue
            if message.error():
                print("Consumer error: {}".format(message.error()))
                continue
            message_username = message.key().decode('utf-8')
            if message_username == username:
                latest_password = message.value().decode('utf-8')
                # break  # Exit the loop once we find the latest password
    finally:
        consumer.close()
    return latest_password

def admin_produce_message_to_topic(topic: str, message: str, answer: str = None):
    configp = {
        'bootstrap.servers': 'localhost:9092',
        'client.id': 'adminProducer'
    }
    producer = Producer(configp)
    if topic == "questions" and answer != None:
        # Have to sanitize the message here because anything in
        # the questions topic will become a topic 
        message = sanitize_topic_name(message)
        # add the question to the questions topic
        producer.produce(topic="questions", value=message)
        # producer.flush()
        # Create child topic for question
        newTopicMessage = "This is the chat for " + str(message)
        producer.produce(topic=message, value=newTopicMessage)
        # producer.flush()
        # Dont need to sanitize answer since its a kafka key
        # value = question, key = answer
        producer.produce("questions_answers", value = str(answer).lower(), key = str(message))
        producer.flush()
    else:
        print("Entering non questions admin produce")
        # Sanitize topic
        topic = sanitize_topic_name(topic)
        producer.produce(topic=topic, value=message, key=answer)
    producer.flush()

# Function to get routes with a specific prefix
def get_routes_with_prefix(prefix: str):
    routes = []
    for rule in app.url_map.iter_rules():
        if str(rule).startswith(prefix):
            routes.append(str(rule))
    return routes

def fetch_correct_answer(topic):
    # Often called by /produce_message
    # Create a Kafka consumer configuration
    group_id = str(uuid.uuid4())
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': group_id,
        'auto.offset.reset': 'earliest'
    } 
    # Create a Kafka consumer
    consumer = Consumer(conf)
    # Subscribe to the "questions_answers" topic
    consumer.subscribe(['questions_answers'])
    correct_answer = None
    try:
        # Consume messages from the "questions_answers" topic
        while True:
            msg = consumer.poll(1.0)
            
            # Check if the message is None (no message received)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            if msg.key():
                # return "MessageWithKeyFoundIfExitTrue"
                # Decode the key and value from the message
                question_key = msg.key().decode('utf-8')
                answer_value = msg.value().decode('utf-8')

                # # This return ensured that the topic was intact before comparison
                # return topic
                
                # # this return ensured that the msg keys were being decoded
                # return question_key
                
                # # This return ennsured that the key and topic match
                # return str(question_key==topic)
                # Check if the key matches the provided topic
                if question_key == topic:
                    # # Ensure that we enter the loop and answer_value is not None
                    # return "We have entered the loop. Answer Value: " + str(answer_value)
                    correct_answer = answer_value
                    break

    finally:
        # Close the consumer to free up resources
        consumer.close() 
        return correct_answer
def checkForCompleted(topic):
    # Often called by produce_message
    # Create a Kafka consumer configuration
    
    # Create a Kafka consumer for inspecting whether a question has been completed.
    consumer = create_consumer(topic="questions_completed", username=str(session.get("username")))
    completed = False
    try:
        # Consume messages from the "questions_answers" topic
        while True:
            msg = consumer.poll(1.0)
            
            # Check if the message is None (no message received)
            if msg is None:
                # If no message is received, check if the consumer has reached the end of the topic
                # by checking if it is currently assigned partitions and those partitions are empty
                if consumer.assignment() and consumer.assignment().is_empty():
                    break  # No more messages in the topic, so break the loop
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            # If we find the topic is in the completed list
            if msg.value().decode('utf-8')==topic:
                completed = True
                break
    finally:
        # Close the consumer to free up resources
        consumer.close() 
        return completed
############################## END FUNCTION DECLARATIONS ##############################   
### Initialize Dictionary to store usage statistics
# This is the one global I couldnt get away from
usage_stats = {}
### Begin Flask Routes
# Track usage statistics
@app.before_request
def track_request():
    global usage_stats
    """Track each request to the application."""
    # Kafka producer configuration
    kafka_producer_config = {
        'bootstrap.servers': 'localhost:9092',
        'client.id': 'usage_stats_producer'
    }
    producer = Producer(kafka_producer_config)
    endpoint = request.endpoint
    if endpoint:
        # Save stats since app start for servicing worker
        if endpoint not in usage_stats:
            usage_stats[endpoint] = 0
        usage_stats[endpoint] += 1
        # Save zookerper lifetime stats in kafka
        message = json.dumps({"endpoint": endpoint})
        producer.produce("usagestatistics", message)
        producer.flush()
    else:
        producer.flush()

@app.route("/")
def index():
    # Look for session username, send to login if theres not one
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))
    return render_template("index.html")

# @app.route("/")
# def home():
#     # This is where the logic for selecting the topic would go
#     topic_name = "exampleTopicNew"
#     return redirect(url_for("riddle", topic=topic_name))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        stored_password = get_user_password(username, "Unknown_User")
        if stored_password == password:
            session["username"] = username
            return redirect(url_for("index"))

        return "Invalid username or password"

    return render_template("login.html")

@app.route("/riddle")
def riddle():
    # Request topic
    topic = request.args.get("topic")
    if not topic:
        return "No topic provided"
    
    return render_template("chatProtoGen.html", topic=topic)

### Produce Message Start ##########################
## Archive
    # We used to repost to the questions_answers topic when the game was over
    # but for now this is cancelled.  
    # # If correct answer = gameover the game is already done. Dont produce.
    # if correct_answer == "gameover":
    #     return redirect(url_for("riddle", topic=topic))
## Description: This function produces messages from users to try to guess the anser to topics
@app.route("/produce_message", methods=["POST"]) 
def produce_message():
    guess = request.form.get("guess")
    topic = request.form.get("topic")

    # return "topic:" + str(topic)+ "guess:" + str(guess)
    # This return confirms that we are recieving the guess and topic

    if not guess or not topic:
        return "No guess or topic provided"
    # Look for session username, shouldnt be here without one so can search
    #  for this username to detect fraudulent messages
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))
    
    # return "Username Verified"

    # Use the username of who sent it to key it to their account
    topic = sanitize_topic_name(topic)

    # # This return ensured sanitize_topic_name isnt deleting the topic data
    # return str(topic)

    # Now we need to Check "questions_completed" to see if the game is done
    # If it is done redirect back to /riddle of the same topic  
    completed = checkForCompleted(topic)
    if completed==True:   
        return redirect(url_for("riddle", topic=topic))
    else:
        # Else the topic is not completed
        # If it is not done check to see if we have the right answer
        # Fetch the correct answer from the "questions_answers" topic
        correct_answer = fetch_correct_answer(topic)
        if not correct_answer:
            return "Could not fetch the correct answer"
        # # This return ensure that fetch_correct_answer isnt deletingn our data
        # return str(correct_answer)
        configp = {
            'bootstrap.servers': 'localhost:9092',
            'client.id': username
        }
        producer = Producer(configp)
        # return "Making it to guess checking"

        # If we have the right answer post the topic to the questions_completed topic and post victory in topic
        # Compare the guess with the correct answer
        if guess.lower() == correct_answer.lower():
            # If the guess is correct, proceed to post victory, and gameover
            victory = str(username)+ " has figured it out! The answer is:" + str(correct_answer)
            producer.produce(topic, value=victory, key=username)
            producer.flush()
            # Produce to questions_answers, value = answer, key = question
            producer.produce(topic="questions_completed", value=topic, key=username)
            producer.flush()
            return redirect(url_for("riddle", topic=topic))
        # if we do not have the right answer post the guess in chat
        else:
            # If the guess is incorrect, print wrong guess to chat
            producer.produce(topic=topic, value=guess, key=username)
            producer.flush()
            return redirect(url_for("riddle", topic=topic))

@app.route("/get_messages/<topic>")
def get_messages(topic):
    sender = session.get("username")
    return Response(kafka_message_generator(topic, sender), mimetype='text/event-stream')

@app.route("/admin_get_messages/<topic>")
def admin_get_messages(topic):
    sender = session.get("username")
    return Response(admin_kafka_message_generator(topic, sender), mimetype='text/event-stream')

@app.route("/admin_dashboard")
def admin_dashboard():
    username = session.get("username")
    # If not admin get em out of here
    if username != "admin":
        return redirect(url_for("index"))
    admin_routes = get_routes_with_prefix("/admin_")
    filtered_admin_routes = [route for route in admin_routes if not route.endswith("<topic>")]
    return render_template("admin_dashboard.html", admin_routes=filtered_admin_routes)

@app.route("/admin_create_question", methods=["GET", "POST"])
def admin_create_question():
    username = session.get("username")
    # If not admin get em out of here
    if username != "admin":
        return redirect(url_for("index"))
    # Else if admin
    if request.method == "POST":
        question = request.form.get("question") # Retrieve question from form
        answer = request.form.get("answer") # Retrieve answer from form
        # If question exists
        if question:
            # Function to produce messages to a topic
            admin_produce_message_to_topic("questions", question, answer)
            return redirect(url_for("admin_create_question"))
    return render_template("adminTopicAdd.html")

@app.route('/admin_usage_stats')
def admin_usage_stats():
    global usage_stats
    username = session.get("username")
    # If not admin get em out of here
    if username != "admin":
        return redirect(url_for("index"))
    # Sort the stats by usage
    sorted_stats = sorted(usage_stats.items(), key=lambda x: x[1], reverse=True)
    return render_template('usage_stats.html', stats=sorted_stats)

@app.route('/admin_topics')
def admin_topics():
    username = session.get("username")
    # If not admin get em out of here
    if username != "admin":
        return redirect(url_for("index"))
    topics = list_topics()
    return render_template('admin_topics.html', topics=topics)

@app.route('/admin_delete_topic/<topic>', methods=['POST'])
def delete_topic(topic):   
    username = session.get("username")
    # If not admin get em out of here
    if username != "admin":
        return redirect(url_for("index"))
    conf = {'bootstrap.servers': 'localhost:9092'}
    admin_client = AdminClient(conf)

    # Initiate the deletion of the topic
    fs = admin_client.delete_topics([topic])

    # Wait for the deletion to complete
    for topic, f in fs.items():
        try:
            f.result() # The result itself is None
            flash(f"Topic {topic} has been deleted successfully.")
        except Exception as e:
            flash(f"Failed to delete topic {topic}: {e}")
    return redirect(url_for('admin_topics'))

### TODO Add view messages logic
@app.route('/admin_view_messages/<topic>')
def view_messages(topic):
    # Implement message viewing logic here
    return render_template('admin_view_messages.html', topic=topic)

if __name__ == "__main__":
    print(Initiazlize_Topic("questions"))
    print(Initiazlize_Topic("users"))
    print(Initiazlize_Topic("questions_completed"))
    app.run(debug=True)

# ### The Nuclear Option
# def delete_all_topics():
#     conf = {'bootstrap.servers': 'localhost:9092'}
#     admin_client = AdminClient(conf)

#     # Get the list of topics
#     topics = admin_client.list_topics().topics.keys()

#     # Delete all topics
#     for topic in topics:
#         admin_client.delete_topics([topic])

# delete_all_topics() 
