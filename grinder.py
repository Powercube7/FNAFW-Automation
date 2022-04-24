from tabnanny import verbose
import pyautogui
import os
from PIL.ImageGrab import grab as grabScreenshot
import functions
import keyboard
import torch

previousKey = None
previousStatus = None
victories = 0
challengers = 0

if not functions.checkFirstTimeUse():
    pyautogui.alert(title="Setup complete", text="First time use setup completed. Enjoy the program!")

print("User Data found. Starting program...")
if not functions.isGameOpened():

    # Read the exePath from the user data file and save it in the variable "gamePath"
    dataFile = open("user.data", "r")
    gamePath = dataFile.read()
    gamePath = gamePath.split("\n")[0]
    gamePath = gamePath.replace("exePath=", "")

    try:
        os.system(f"start {gamePath}")
        print("Game opened successfully. Starting modules.")
    except:
        print("Game could not be opened. Please make sure the game is installed and the path is correct.\fIf the path isn't correct, delete user.data and restart the program.")
else:
    print("Game already open. Starting modules.")

# Load the modules
fight, roam = functions.enableModules()
modules = functions.Modules

# Load AI Model
if fight or roam:
    print("Loading AI model...")
    model = torch.hub.load("ultralytics/yolov5", "custom", "./assets/FNAF.pt", verbose = False, _verbose = False)
    model.conf = 0.7
    print("\nAI Model loaded successfully")
    yoloActions = functions.InputActions(model)
else:
    print("\nNo modules enabled. Exiting program.")
    raise SystemExit("No modules enabled. Program execution stopped.")

print(f"Automatic Fighting Engaged: {fight}")
print(f"Automatic Roaming Engaged: {roam}")
while not keyboard.is_pressed('q'):

    # Take a screenshot of the game and get the status using the AI's detections
    frame = grabScreenshot()
    resultImage, parameters = yoloActions.runInference(frame, True, True)
    currentStatus = yoloActions.getCurrentStatus(parameters)

    # If E is being held, check if switch button and health is visible
    if keyboard.is_pressed('e'):
        if "Switch Button" in parameters["name"] and "Health" in parameters["name"]:
            switchButton = functions.getCenter(parameters["name"].index("Switch Button"), parameters)
            pyautogui.moveTo(switchButton)
            pyautogui.click()
    else:
        # Run actions based on the enabled modules
        if fight:
            modules.AutoFight(parameters, currentStatus)
        if roam:
            previousKey = modules.AutoRoam(currentStatus, previousKey, parameters)

        # Increment the total victories if the user won
        if currentStatus == 'Battle End Screen' and previousStatus != currentStatus:
            victories += 1

        # Increment the total challengers if the user encountered one
        if currentStatus == 'Encountered Challenger' and previousStatus != currentStatus:
            challengers += 1

    previousStatus = currentStatus
pyautogui.alert(title="Program ended", text= f"Total battles won: {victories}\nTotal challengers encountered: {challengers}")