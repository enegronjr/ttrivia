import os

import openai
from flask import Flask, redirect, render_template, request, url_for

from PIL import Image
from pytesseract import Output
import pytesseract
import cv2
import numpy as np
import os
import sys

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        question = "Which company in the U.S. had the biggest revenue in 2022?"
        questionChoices = ["Walgreens", "Target", "Walmart"]
        scanQuestion = ""
        scanChoices = ["", "", ""]
        
        os.system("cp /mnt/d/MirrorGo/ScreenShot/* image.png")
        filename = "/home/eddien/Documents/tiktokTrivia/image.png"
        image = cv2.imread(filename)
        resultstr = pytesseract.image_to_string(image, output_type=Output.DICT)
        results = pytesseract.image_to_data(image, output_type=Output.DICT)
        for i in range(0,len(results["text"])):
            x = results["left"][i]
            y = results["top"][i]
            w = results["width"][i]
            h = results["height"][i]

            text = results["text"][i]
            conf = int(results["conf"][i])

            if conf > 70:
                text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
                if x >= 130 and x <=750 and y >= 640 and y <= 900:
                    scanQuestion += (text + " ")
                if x >= 145 and x <=750 and y >= 960 and y <= 1030:
                    scanChoices[0] += (text + " ")
                if x >= 145 and x <=750 and y >= 1100 and y <= 1185:
                    scanChoices[1] += (text + " ")
                if x >= 145 and x <=750 and y >= 1255 and y <= 1325:
                    scanChoices[2] += (text + " ")
    
        
        print(results)
        print(resultstr)
        scanQuestion = scanQuestion[:-1]
        scanChoices[0] = scanChoices[0][:-1]
        scanChoices[1] = scanChoices[1][:-1]
        scanChoices[2] = scanChoices[2][:-1]
        print(scanQuestion)
        print(scanChoices)

        cv2.rectangle(image, (130, 640), (750, 900), (0, 255, 0), 2)
        cv2.rectangle(image, (145, 960), (750, 1030), (0, 255, 0), 2)
        cv2.rectangle(image, (145, 1100), (750, 1185), (0, 255, 0), 2)
        cv2.rectangle(image, (145, 1255), (750, 1325), (0, 255, 0), 2)
        cv2.imwrite("modifiedImg.png", image)

        os.system("mv /mnt/d/MirrorGo/ScreenShot/* /mnt/d/MirrorGo/archive/ && rm image.png")

        if "NOT" in scanQuestion or "not" in scanQuestion:
            qprompt = generateNotPrompt(scanQuestion, scanChoices)
        else:
            qprompt = generatePrompt(scanQuestion, scanChoices)

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=qprompt,
            temperature=0.6,
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generatePrompt(question, questionChoices):
    return '''Select the correct answer to the question from the list of possible answers. Only respond with the answer.
        Q: Bougainville is set to become a nation after it gains independence from what?
        Choices: Australia, Brazil, Papua New Guinea
        Answer: Papua New Guinea
        Q: Where do Nintendo's Mario & Luigi reside?
        Choices: Wonderland, Japan, Mushroom Kingdom
        Answer: Mushroom Kingdom
        Q: A popular genetic genealogy company is named for a human's being's number of what?
        Choices: Genes, Chromosomal pairs, Nucleotides
        Answer: Chromosmal pairs
        Q: {}
        Choices: {}, {}, {}
        Answer:'''.format(question.capitalize(), questionChoices[0].capitalize(), questionChoices[1].capitalize(), questionChoices[2].capitalize())

def generateNotPrompt(question, questionChoices):
    return '''Select the correct answer to the question from the list of possible answers. Only respond with the answer.
        Q: Which of these is NOT a pasta dish?
        Choices: Cacio e pepe, Castiglione, Culurgiones
        Answer: Castiglione
        Q: The term "Oblique" would NOT normally be used to describe which of these?
        Choices: Angle, Muscle, Transparency
        Answer: Transparency
        Q: Who was NOT a core cast member on "Gumpy"?
        Choices: Clokey, Goo, Prickle
        Answer: Clokey
        Q: {}
        Choices: {}, {}, {}
        Answer:'''.format(question.capitalize(), questionChoices[0].capitalize(), questionChoices[1].capitalize(), questionChoices[2].capitalize())
