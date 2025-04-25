import requests
import sys
import time

def list_compound_glycan():
    """
    Extract and process list of compounds and glycans

    sqlite: .mode tabs
    sqlite: .import KEGG_compound_glycan.tsv compound_glycan
    """
    f = requests.get("https://rest.kegg.jp/list/compound").text + requests.get("https://rest.kegg.jp/list/glycan").text
    f = f.split("\n")
    f = [x.split("\t") for x in f]
    f = [x for x in f if len(x) == 2]
    f = [(x[0].strip(), x[1].strip()) for x in f]
    outfile = open("KEGG_compound_glycan.tsv", "w")
    for x in f:
        # ["ID", "name"]
        outfile.write("\t".join(x) + "\n")
    outfile.close()

def reactions():
    """
    Extract and process reactions data; including reactants, products, and enzymes

    sqlite: .mode tabs
    sqlite: .import KEGG_reaction_data.tsv reactions
    sqlite: .import KEGG_reaction_enzymes.tsv reaction_enzyme_map
    """
    # Get list of reactions
    f = requests.get("https://rest.kegg.jp/list/reaction").text
    f = f.split("\n")
    f = [x.split("\t") for x in f]
    f = [x for x in f if len(x) == 2]
    f = [(x[0].strip(), x[1].strip()) for x in f]
    # Process list of reactions into dictionary
    data = {}
    for x in f: data[x[0]] = {'definition_1': x[1]}
    print("%i reactions obtained" % int(len(data)))
    # Process reaction data into dictionary
    for reactionID in data:
        f = requests.get("https://rest.kegg.jp/get/%s" % reactionID).text
        f = f.split("\n")
        try: 
            name = [x for x in f if x.startswith("NAME")][0][12:]
            data[reactionID]["name"] = name
        except: 
            name = "PROCESSING_ERROR"
            data[reactionID]["name"] = name
        try: 
            definition = [x for x in f if x.startswith("DEFINITION")][0][12:]
            data[reactionID]["definition_2"] = definition
        except: 
            definition = "PROCESSING_ERROR"
            data[reactionID]["definition_2"] = definition
        try: 
            equation = [x for x in f if x.startswith("EQUATION")][0][12:]
            data[reactionID]["equation"] = equation
        except: 
            equation = "PROCESSING_ERROR" 
            data[reactionID]["equation"] = equation
        try:
            reactants = equation.split(" <=> ")[0]
            reactants = equation.split(" <=> ")[0].split(" + ")
            d = []
            for x in reactants:
                if len(x.split(" ")) == 1: d.append(x)
                elif len(x.split(" ")) == 2: d.append(x.split(" ")[1])
            data[reactionID]["reactants"] = " + ".join(d)
            products = equation.split(" <=> ")[1]
            products = equation.split(" <=> ")[1].split(" + ")
            d = []
            for x in products:
                if len(x.split(" ")) == 1: d.append(x)
                elif len(x.split(" ")) == 2: d.append(x.split(" ")[1])
            data[reactionID]["products"] = " + ".join(d)
        except: 
            data[reactionID]["reactants"] = "PROCESSING_ERROR"
            data[reactionID]["products"] = "PROCESSING_ERROR"
        try:
            enzyme = [x for x in f if x.startswith("ENZYME")][0][12:]
            data[reactionID]["enzyme"] = [x.strip() for x in enzyme.split()]
        except:
            data[reactionID]["enzyme"] = ["PROCESSING_ERROR"]
        print("Reaction %s processed: %s -> %s" % (reactionID, data[reactionID]["reactants"], data[reactionID]["products"]))
        time.sleep(0.75)
    # Output reaction data into files
    outfile = open("KEGG_reaction_data.tsv", "w")
    for reactionID in data:
        # ["reaction_ID", "name", "reactants", "products", "equation", "definition_RL", "definition_R"]
        x = [reactionID, data[reactionID]["name"], data[reactionID]["reactants"], data[reactionID]["products"], data[reactionID]["equation"], data[reactionID]["definition_1"], data[reactionID]["definition_2"]]
        if "PROCESSING_ERROR" in x: pass
        else: outfile.write("\t".join(x) + "\n")
    outfile.close()
    outfile = open("KEGG_reaction_enzymes.tsv", "w")
    for reactionID in data:
        for enzymeID in data[reactionID]["enzyme"]:
            # ["enzyme_EC", "reaction_ID"]
            x = [enzymeID, reactionID]
            if "PROCESSING_ERROR" in x: pass
            else: outfile.write("\t".join(x) + "\n")
    outfile.close()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        list_compound_glycan()
        reactions()
    elif len(sys.argv) == 2:
        command = sys.argv[1]
        if command.lower() == "cg": list_compound_glycan()
        elif command.lower() == "reaction": reactions()
