import random

def main():

    # 1. Load names/availability from sheet
    people = {}
    people = read()
    siblingList = getSiblings()

    # 2. Add | Delete Names/availability
    loadData = True
    cont = input("Add/Delete New Person? 1:Yes | 0:No ")
    if int(cont) == 0:
        loadData = False
    while loadData:

        name = input("Enter name: ")
        
        addOrDelete = input("1:Add | 2: Delete ")
        if int(addOrDelete) == 2:
            delete(name) #TODO

        elif int(addOrDelete) == 1:
            add(name)

        cont = input("Add/Delete New Person? 1:Yes | 0:No ")
        if int(cont) == 0:
            loadData = False

    people = read()
    siblingList = getSiblings()
    availability = createAvailability(people)

    a = input("View? 1:Yes | 0:No ")
    if int(a) == 1:
        view(people, siblingList, availability)

    # 3. allow a quit
    q = input("Quit? 1:Yes | 0:No ")
    if int(q) == 1:
        return

    tracker = {} # TODO keep tracker to determine whos not picked
    for k in people.keys():
        tracker[k] = 0

    print(tracker)

    # weeks = input("Enter the number of weeks: ")
    weeks = 30
    workedPastWeeks = []
    sessions = 5
    for wk in range(weeks):

        print("Week: ",wk)
        workedPast2Weeks = workedPastWeeks[-2:]
        workedToday = []
        for sess in range(sessions):

            availableList = getAvailablePeople(availability[sess], workedPast2Weeks, workedToday)
            #print(availableList)

            leastWorked = getLeastWorked(tracker,availableList, siblingList)
            #print(leastWorked)

            # Add to list / tracker / worked today
            tracker = addToTracker(tracker, leastWorked)
            workedToday.append(leastWorked)
            print(leastWorked)

        workedPastWeeks.append(workedToday)

    #print(workedPastWeeks)
    print(tracker)
    takePDF(workedPastWeeks)

def takePDF(schedule):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    timeHelp = {
            1:"1600",
            2:"0730",
            3:"0900",
            4:"1045",
            5:"1230"
        }

    week = 1
    for wk in schedule:

        s = f"Session {week}"
        pdf.cell(200,10,txt=s, ln=1, align='L') #Txt
        t_slot = 1
        for sesh in wk:

            list_string = ','.join(sesh)
            new_S = f"{timeHelp[t_slot]}: {list_string}"
            pdf.cell(200,10,txt=new_S,ln=1,align='L')
            t_slot += 1
        week += 1
    pdf.output("list_output.pdf")


def getSiblings():

    holder = {}
    with open("people.txt", "r") as file:
        for line in file:
            # Process each line
            xList = line.split(",")

            # Sibling hit
            group = int(xList[2])
            if group > 0:

                if group in holder:
                    l = holder[group]
                    l.append(xList[0])
                    holder[group] = l
                else:
                    l = []
                    l.append(xList[0])
                    holder[group] = l

    #print(holder)
    return holder


def addToTracker(tracker, worked):
    
    for person in worked:

        if person in tracker:
            timesWorked = tracker[person]
            timesWorked += 1
            tracker[person] = timesWorked
        else:
            tracker[person] = 1

    return tracker

def getLeastWorked(tracker, availableList, siblings):
    #print("least worked")
    peopleToSched = []

    availTracker = {}
    for person in tracker:

        if person in availableList:
            availTracker[person] = tracker[person]

    availSibs = {}
    for groupNo in siblings:

        addGroup = False
        for person in siblings[groupNo]:
            if person in availableList:
                addGroup = True
        
        if addGroup:
            availSibs[groupNo] = siblings[groupNo]

    # Get 3 last in tracker
    # Check siblings
    print(availTracker)
    sorted_tracker = sorted(availTracker, key=availTracker.get)
    print(sorted_tracker)
    
    # if all(value == 0 for value in availTracker.values()):
    #     random.shuffle(sorted_tracker)
    #print(sorted_tracker)

    if len(sorted_tracker) <= 3:
        for k in range(len(sorted_tracker)):
            peopleToSched.append(sorted_tracker[k])
        return peopleToSched
        
    while len(peopleToSched) < 3:

        # Check last 3 if one is siblings add sibs then fill till 3
        # else add last 3
        first3 = sorted_tracker[:3]
        #print(first3)

        siblingHit = False
        groupNum = 0
        for person in first3:
            
            for groupNo in availSibs:
                people = availSibs[groupNo]
                if person in people:
                    groupNum = groupNo
                    siblingHit = True
                    break
            if siblingHit:
                break
        
        if siblingHit:
            
            # Add siblings
            # Check len
            # Get next person in last 3
            people = availSibs[groupNum]
            for person in people:
                peopleToSched.append(person)

            

            if len(peopleToSched) < 3:

                # TODO Make sure to not get another sib ^fix
                sibsNames = []
                for groupNum in availSibs:
                    people = availSibs[groupNum]
                    for person in people:
                        sibsNames.append(person)
                l3 = [x for x in sorted_tracker if x not in peopleToSched]
                l3 = [x for x in l3 if x not in sibsNames]
                if l3:
                    peopleToSched.append(l3[0])
                    return peopleToSched
            else:
                return peopleToSched

        else:
            return first3



def getAvailablePeople(availPeople, workedPast2Weeks, workedToday):
    
    newL = []
    holderL = {}

    # worked Today
    for person in availPeople:

        worked = False
        for sess in workedToday:
            if person in sess:
                worked = True
        
        if not worked:
            newL.append(person)

    # Worked past 2 weeks
    for wk in workedPast2Weeks:
        for sess in wk:
            for p in sess:

                if p in holderL:
                    timesWorked = holderL[p]
                    timesWorked += 1
                    holderL[p] = timesWorked
                else:
                    holderL[p] = 1

    deleteList = []
    for person in holderL.keys():
        times = holderL[person]
        if times == 2:
            deleteList.append(person)

    l3 = [x for x in newL if x not in deleteList]

    return l3


def createAvailability(people):
    
    holder = {0:[], 1:[], 2:[],3:[],4:[]} # STATIC set to 5 time slots
    for person in people:

        personTime = people[person]
        timeSlotCnt = 0
        for timeSlot in personTime:

            personTimeSlot = personTime[timeSlot]
            if personTimeSlot == 1:

                slotList = holder[timeSlotCnt]
                slotList.append(person)
                holder[timeSlotCnt] = slotList

            timeSlotCnt += 1

    return holder


def view(people, siblingList, availability):
    
    print("People:")
    for k in people.keys():
        print(f"{k}: {people[k]}")
    print("\nSiblings:")
    for k in siblingList.keys():
        print(f"{k}: {siblingList[k]}")
    print("\nAvailability:")
    for k in availability.keys():
        print(f"{k}: {availability[k]}")


def delete(name):

    # Search name in file
    # Remove name
    try:
        with open('people.txt', 'r') as fr:
            lines = fr.readlines()

            with open('people.txt', 'w') as fw:
                for line in lines:

                    xList = line.split(",")
                    if xList[0] != name:
                        fw.write(line)

        print("Deleted")
    except:
        print("Oops! something error")
    pass

def read():

    holder = {}
    with open("people.txt", "r") as file:
        for line in file:
            # Process each line
            xList = line.split(",")

            avail = {}
            cnt = 0
            for i in xList[1]:
                if i == "1":
                    avail[cnt] = 1  # True
                elif i == "0":
                    avail[cnt] = 0  # False
                cnt += 1

            holder[xList[0]] = avail

    #print(holder)
    return holder

def add(name):

    # Get schedule
    s = ""
    for i in range(5):
        tSlot = input(f"Enter availability for timeslot {i+1} 1:Yes | 0:No ")
        s += tSlot

    # Sibling
    yesSib = input("1: Sibling | 0: No Sibling: ")
    if int(yesSib) == 1:
        sibGroup = input("Enter Sibling group: ")

    # Add name, schedule, siblings
    with open("people.txt", "a") as f:

        writeString = ""
        if int(yesSib) == 1:
            writeString = name + "," + s + "," + sibGroup + "\n"
        else:
            writeString = name + "," + s + "," + "0\n"

        f.write(writeString)


if __name__ == "__main__":
    main()