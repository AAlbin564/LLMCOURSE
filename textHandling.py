

matchingLinks = []
filepath = "rawText.txt"

file = open(filepath, "r")

#vi vill kanske spara ar-programmet-ratt-for-dig senar kan diskuteras
#vad händer efter studierna kanske också kan vara bra men bör segmenteras ut 
for line in file:
    if "https://www.uu.se/utbildning/program/" in line and "mer-infor-anmalan" not in line and "ar-programmet-ratt-for-dig" not in line and "vad-hander-efter-studierna" not in line:

        matchingLinks.append(line)
file.close()

for link in matchingLinks:
    print(f"{link}\n")

with open("links.txt", "w", encoding="utf-8") as f:
    for link in matchingLinks:
        print(link)           
        f.write(f"{link}\n") 

