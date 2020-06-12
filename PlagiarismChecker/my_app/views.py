from django.shortcuts import render
from django.http import HttpResponse
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

#to render homepage
def home(request):
    return render(request,'homepage/homepage.html')

#to render login page
def login(request):
    return render(request, 'login/login.html')


superUsername="" #Declaring Global Varaible to be used while creating Database filename if they wish to add the file in Database

#the process of validating login,and giving out proper responses
def loginLogic(request):
    found=0 #if the user is found in login database found is initialized as 1
    logindatabase=open('userdatabase.txt') #opening user login database
    global superUsername #to use global variable in the function
    loginbuffer=request.POST['username']+'|'+request.POST['password'] #reading out the username and password from the login html page and seperating with a delemiter because thats how files are saved in database
    superUsername=request.POST['username'] #initializing the global variable so that it can be used later on
    for user in logindatabase:#iterating to each user in login Database
        if user.strip()==loginbuffer: #strip is used to remove the extra spaces i.e /n from that line,and we check if that is same as the entered value, the value entered database is also of the form username/password
            found=1 #if the value entered matches userdatabase we initialize found =1
    LoginDict={ #we create dictonary to pass it to the html so that we can tell hello {username} login SUCCESSFUL
    'username':superUsername,
    }
    if(found==1):
        return render(request, 'plagiarism/plagiarism.html',LoginDict) #if the login is SUCCESSFUL we render the next page that is where to upload the file, but first we till hello username login SUCCESSFUL
    else:
        return render(request, 'login/wrongLogin.html') #if the login fails we render wrong login page and ask them to login again

#to render register page
def register(request):
    return render(request, 'register/register.html')

#the process of validating if the username is not repeated and later adding them in userdatabase
def registerlogic(request):
    found=0  ##if the user already exists in login database, if yes found is initialized as 1
    logindatabase=open('userdatabase.txt','r') #opening user login database
    registerusername=request.POST['username'] #reading the register USERNAME from HTML
    registerbuffer=request.POST['username']+'|'+request.POST['password']+'\n' #reading the username and password from HTML and seperating with  delemiter
    for user in logindatabase: #for checking if the user already exists in the user database
        userlist=user.split('|') #seperating the username from password with the given delemiter
        if userlist[0]==registerusername:  #taking the username frm the list and checking if it is same as the username entered in html
            found=1 #if yes initialize with 1
    logindatabase.close()
    if(found==1):  #if user already exits render wrong register html and ask them to login again
        return render(request, 'register/wrongRegister.html')
    else: #if the user doesnt exits and the user and password in the login database
        logindatabase=open('userdatabase.txt','a')
        logindatabase.write(registerbuffer)
        return render(request, 'login/registerSucess.html') #and render login page with registration success message

superFile=None  #Declaring global variable to get the filename used by the user to be used later if the user wish to add the file in the database
superList=[] #to store each line from the file entered by the user to be used later if they wish to save in database

#once the file is uploaded the plagiarism checking happens here
def postUpload(request):
    #to use gloabal variable in the function
    global superFile
    global superList
    file = request.FILES['sentFile'] #the get the file uploaded by the user
    superFile=file.name #to get the file name of the file entered to be used later if the wish to save the file

    #code to save the file in a particular directory along with its content, i made a buffer directory to save the file
    path = default_storage.save(f'bufferFolder/{file.name}', ContentFile(file.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    file=open(f'bufferFolder/{file.name}') #opening the file saved in read mode

    bufferlines=[] #to seperate file to list of sentences

    for line in file:
        superList.append(line) #saving the list of lines in the global SuperLines to be used later if the user wish to save the file
        sentences=line.split('.') #splting each lines with . delimeter to form sentences
        bufferlines.extend(sentences) #adding this to the list of sentences
    file.close()
    os.remove(f'{file.name}') #deleting the file in the buffer folder, becase same filenames will create problems
    bufferlinewords=[] #to seperate senetnces to list of words
    for line in bufferlines:  #for each line is the setences list
        bufferwords=line.split(' ') #seperate words with space delemiter
        if(bufferwords!=['\n']): #removing the empty lines which just as only \n without any content
            bufferlinewords.append(bufferwords) #appending the entire list of words to the list so it forms [[sentence1Word1,sentence1Word2],[senetnce2Word1,sentence2Word2],etc]
    for linewords in bufferlinewords: #for each list conatining the list of words in the MAIN LIST
        if len(linewords)<=3: #deleting lines which contains 3 or lesser words
            bufferlinewords.remove(linewords)
    LineCheck=[] #to see how many senetnces are plagiarized for overall Percentage
    LineCount=len(bufferlinewords) #to count total number of sentences
    for i in range(LineCount): #making list equal to number of lines and initializing eachline to not plagiarized
        LineCheck.append(0)
    directory='fileDatabase' #our file database directory
    OutputList=[] #a list containing set of statements to be displayed in HTML

    for filename in os.listdir(directory): #for each file in the file database
        file=open(f'fileDatabase/{filename}') #opening that file
        bufferlines=[] #same process as above for a different file,refer from line 75
        for line in file:
            sentences=line.split('.')
            bufferlines.extend(sentences)
        file.close()
        destBufferlinewords=[]
        for line in bufferlines:
            bufferwords=line.split(' ')
            if(bufferwords!=['\n']):
                destBufferlinewords.append(bufferwords)
        for linewords in destBufferlinewords:
            if len(linewords)<=3:
                destBufferlinewords.remove(linewords)
        allCount=0 #for number of lines plagiarized in each file
        allTotal=0 #to iterate through the line and keep count of which line being executed and to find total number of lines
        for eachline in bufferlinewords: #for each line in the file entered by the user
            allTotal+=1 #to iterate through the line and to find total number of lines
            for destEachline in destBufferlinewords: #for eachline in the database file
                count=0 #to check how many words in a user line is there in dest vfile line
                total=0 #total number of words in a user line
                for eachword in eachline:
                    total+=1 #to count number of words in user line
                    if eachword in destEachline: #to check if the word is there dest line
                        count+=1
                if (count/total)>=.80: #if 80 percent of user entered line is present in destination file line
                    allCount+=1 #increase the plagiarized line by 1
                    LineCheck[allTotal-1]=1 #making that line already plagiarized for the Overall plagiarism Percentage
                    break #if a line is plagiarized no need to check in other lines of the same file hence stop the itertaion and go to next line
        if(allTotal!=0):
            percentPlag=allCount/allTotal*100 #to find percent plagir from each file
            OutputList.append(f"The Percentage Plagiarism from {filename} is %.2f"%percentPlag) #Append this in the OutputList so that we can print it in HTML

    FinalPlagCount=0 #To check how many lines in Line Check are 1, basically to see how many lines are overall plagiarized
    for each in LineCheck: #to check how many lines have 1
        if each==1:
            FinalPlagCount+=1
    FinalOutput="NULL"
    if(LineCount!=0):
        OverallPercentPlag=FinalPlagCount/LineCount*100 #the overall Plagiarism Percentage
        FinalOutput=(f"The Overall Percentage Plagiarism is %.2f"%OverallPercentPlag) #for the HTML print statements
    else:
        FinalOutput=f"Your File {superFile} is empty "
    OutputDict={  #its dictonary to send the OutputList to tht HTML to use it in the front end
    "OutputList":OutputList,
    "FinalOutput":FinalOutput,
    }
    return render(request,"plagiarism/plagiarismOutput.html",OutputDict) #we render the Plagiarism Output HTML and we pass the dict to be printed in OP

#to add the file to the File Database
def addFile(request):
    OutputStatement={
    'username':superUsername,
    'filename':superFile,
    }
    if(request.POST['include']=='YES'): #to check if the user entered yes for the add file in Database
        filename=superUsername+"'s "+str(superFile) #using the global variable to form a new file name, username +actual filename
        file=open(f'fileDatabase/{filename}','a') #creating a new file with the our new filename and using append func
        for line in superList: #using gloabal variable to get each line from the user file
            file.write(line) #writing line to our new files
        return render(request,'FinalPage/FileAdded.html',OutputStatement) #rendering file added SUCCESSFULLY message
    else:

        return render(request,'FinalPage/ThankYou.html',OutputStatement) #if they choose no to add files then rendering thank you message

#THANK YOU | A PROJECT BY TABIH,MOIN AND RAYYAN
