from Bio import SeqIO
import csv

def extract_cds_to_csv(genbank_file, output_csv):
    record = SeqIO.read(genbank_file, "genbank")
    
    cds_list = []
    for feature in record.features:
        if feature.type == "CDS":
            protein_id = feature.qualifiers.get("protein_id", [""])[0]
            locus_tag = feature.qualifiers.get("locus_tag", [""])[0]
            gene = feature.qualifiers.get("gene", [""])[0]
            ec_number = feature.qualifiers.get("EC_number", [""])
            ec_number = ec_number[0] if ec_number else ""
            cds_list.append([protein_id, locus_tag, gene, ec_number])
    
    # Write to CSV
    with open(output_csv, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["protein_id", "locus_tag", "gene", "EC_number"])  # Header
        writer.writerows(cds_list)

    print(f"Exported {len(cds_list)} CDS entries to {output_csv}")

if __name__ == '__main__':
    import sys
    extract_cds_to_csv(sys.argv[1], sys.argv[2])
