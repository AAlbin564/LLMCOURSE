
matching_links = []
filepath = "sitemap_links.txt"

with open(filepath, "r", encoding="utf-8") as file:
    for line in file:
        if "https://www.uu.se/utbildning/program/" in line and "ar-programmet-ratt-for-dig" in line:
            matching_links.append(line)

with open("rattfordig_links.txt", "w", encoding="utf-8") as f:
    for link in matching_links:
        result = link.replace("<loc>", "").replace("</loc>", "").strip()
        print(result)
        f.write(f"{result}\n")
