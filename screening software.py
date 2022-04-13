import os
import json
import pdfplumber
import re
import string
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import shutil

def main():
    """ This method is to get insights from the uploaded resume in .pdf format """
    # Import path
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./..")).replace("\\", "/")
    # Create folder
    if not os.path.exists('db'):os.makedirs('db')
    if not os.path.exists('json'):os.makedirs('json')
    if not os.path.exists('images'):os.makedirs('images')
    if not os.path.exists('dump'):os.makedirs('dump')
    # To get all the .pdf files in "db" folder
    files_pdf=[f for f in os.listdir(path+"/db/") if f.endswith('.' + 'pdf')]
    for filename in files_pdf:
        # Open pdf file
        pdf = pdfplumber.open(path +"/db/"+ filename)
        # Get total number of pages
        num_pages = len(pdf.pages)
        # Initialize a count for the number of pages
        count = 0
        # Initialize a text empty etring variable
        text = ""
        # Extract text from every page on the file
        while count < num_pages:
            pageObj = pdf.pages[count]
            count += 1
            text += pageObj.extract_text()
        # Convert all strings to lowercase
        text = text.lower()
        # Remove numbers
        text = re.sub(r"\d+", "", text)
        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))
        # Create dictionary with industrial and system engineering key terms by area
        terms = json.load(open(path +"/setting/"+"Config.json"))
        # Initialize score counters for each area
        quality=0
        # Create an empty list where the scores will be stored
        scores = []
        # Obtain the scores for each area
        for area in terms.keys():
            for i in range(len(terms.keys())):
                if area == list(terms.keys())[i]:
                    for word in terms[area]:
                        if word in text:
                            quality += 1
                    scores.append(quality)
                    quality =0
        # Create a data frame with the scores summary
        summary = pd.DataFrame(scores, index=terms.keys(), columns=["score"]).sort_values(by="score", ascending=False)
        # Create pie chart visualization
        pie = plt.figure(figsize=(10, 10))
        plt.pie(summary["score"],labels=summary.index,explode=(0.1, 0, 0, 0, 0, 0),autopct="%1.0f%%",shadow=True,startangle=90,)
        plt.title(filename.split(".")[0])
        plt.axis("equal")
        # Save pie chart as a .png file
        pie.savefig(path+"/Images/"+filename.split(".")[0]+".png")
        # Save json file
        json.dump({filename : summary.to_json(orient="columns") },open(path +"/json/"+filename.split(".")[0]+"__result.json","w"))
        # Close opened pdf file
        pdf.close()
        # Dump the file
        shutil.move(path+"/db/"+filename,path+"/dump/"+filename)
    return (print("Success"))

if __name__=="__main__":
    main()
    