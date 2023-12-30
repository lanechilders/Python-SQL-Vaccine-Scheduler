from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)
    


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)
    

def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
   # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict = True)

    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    get_availabities = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username"
    try:
        cursor.execute(get_availabities, d)
        for row in cursor:
            print("Caregiver: " + row['Username']+ " ")
    except pymssql.Error:
        print("Please try again!")
        quit()
    except ValueError:
        print("Please try again!")
        return

    get_vaccines = "SELECT * FROM Vaccines"
    try:
        cursor.execute(get_vaccines)
        for row in cursor:
            print("name: " + str(row['Name'])+ ", available_doses: " + str(row['Doses']))
    except pymssql.Error as e:
        print("Please try again!", e)
        print("Error:", e)
        return
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
        return
    finally:
        cm.close_connection()


def reserve(tokens):

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    global current_caregiver
    global current_patient

    # check 1: see if patient is logged in or not
    if current_patient is None:
        if current_caregiver is not None:
            print("Please login as a patient first!")
        else:
            print("Please login first!")
        return
    
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    date = tokens[1]

    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    vaccine = tokens[2]
    
    get_vaccines = "SELECT * From Vaccines WHERE Doses > 0 AND Name = %s"
    try:
        cursor.execute(get_vaccines, vaccine)
        if cursor.rowcount == 0:
            print("Not enough available doses!")
            return
        for row in cursor:
            chosen_vaccine_name = row['Name']
    except pymssql.Error:
        print("Please try again!")
        return

    find_availabilities = "SELECT TOP 1 Username FROM Availabilities WHERE Time = %s ORDER BY Username"
    try:
        cursor.execute(find_availabilities, d)
        if cursor.rowcount == 0:
            print("No Caregiver is available!")
            return
        for row in cursor:
            care_name = row['Username']
    except pymssql.Error:
        print("Please try again!")
        return
    
    insert_appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s)"
    patient_name = current_patient.get_username()
    try:
        cursor.execute(insert_appointment,(chosen_vaccine_name, care_name, patient_name, d))
        conn.commit()
    except pymssql.Error:
        print("Please try again!") 
        return

    get_appointment_id = "SELECT TOP 1 Appointment_id FROM Appointments WHERE Name = %s AND CUsername = %s AND TIME = %s"
    try:
        cursor.execute(get_appointment_id,(chosen_vaccine_name, care_name, d))
        for row in cursor:
            appointment_id = row['Appointment_id']
            print("AppointmentID : {" + str(appointment_id) + "}, Caregiver username: {" + care_name + "}")
    except pymssql.Error:
        print("Please try again!")
        return  
    
    update_doses = "UPDATE Vaccines SET Doses = Doses - 1 WHERE Name = %s"
    try:
        cursor.execute(update_doses, chosen_vaccine_name)
        conn.commit()
    except pymssql.Error:
        print("Please try again!")
        return  

    update_availabilities = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"
    try:
        cursor.execute(update_availabilities, (d, care_name))
        conn.commit()
    except pymssql.Error as e:
        print("Please try again!")
        print("Error:", e)
        return
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    

def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    
    if len(tokens) != 1:
        print("Please try again")
        return

    if current_caregiver is not None:
        caregiver_name = current_caregiver.get_username()
        get_caregiver_appointments = "SELECT Appointment_id, Name, PUsername, Time FROM Appointments WHERE CUsername = %s ORDER BY Appointment_id"

        try:
            cursor.execute(get_caregiver_appointments, caregiver_name)
            for row in cursor:
                print(str(row['Appointment_id']) + " " + str(row['Name']) + " " + str(row['Time']) + " " + str(row['PUsername']))
        except pymssql.Error as e:
            print("Please try again!")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Please try again!")
            print("Error:", e)
            return

    elif current_patient is not None:
        patient_name = current_patient.get_username()
        get_patient_appointments = "SELECT Appointment_id, Name, CUsername, Time FROM Appointments WHERE PUsername = %s ORDER BY Appointment_id"

        try:
            cursor.execute(get_patient_appointments, patient_name)
            for row in cursor:
                print(str(row['Appointment_id']) + " " + str(row['Name']) + " " + str(row['Time']) + " " + str(row['CUsername']))
        except pymssql.Error as e:
            print("Please try again!")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Please try again!")
            print("Error:", e)
            return
        finally:
            cm.close_connection()
        return

def logout(tokens):
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return 
    
    if len(tokens) != 1:
        print("Please try again")
        return
  
    if current_caregiver is not None:
        current_caregiver = None
        print("Sucessfully logged out!")
        return
    
    if current_patient is not None:
        current_patient = None
        print("Sucessfully logged out!")
        return


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> Enter command: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
            commands()
        elif operation == "create_caregiver":
            create_caregiver(tokens)
            commands()
        elif operation == "login_patient":
            login_patient(tokens)
            commands()
        elif operation == "login_caregiver":
            login_caregiver(tokens)
            commands()
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
            commands()
        elif operation == "reserve":
            reserve(tokens)
            commands()
        elif operation == "upload_availability":
            upload_availability(tokens)
            commands()
        elif operation == cancel:
            cancel(tokens)
            commands()
        elif operation == "add_doses":
            add_doses(tokens)
            commands()
        elif operation == "show_appointments":
            show_appointments(tokens)
            commands()
        elif operation == "logout":
            logout(tokens)
            commands()
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!") 
            commands()
            


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''
    
    def commands (): # list of commands to reprompt the user when a user inputs an invalid command / when they successfully complete a command / if they fail to complete it.
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>") 
        print("> reserve <date> <vaccine>")  
        print("> upload_availability <date>")
        print("> cancel <appointment_id>")  
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  
        print("> logout")  
        print("> Quit")
        print()

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
