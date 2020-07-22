import json

corona_file = './covid19japan.json'

f = open(corona_file)
corona_data = json.load(f)

f.close()

print(corona_data["npatients"])
print(corona_data["nexits"])
print(corona_data["ndeaths"])
print(corona_data["ncurrentpatients"])

