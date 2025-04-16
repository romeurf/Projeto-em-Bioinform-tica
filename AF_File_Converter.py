import os
from Bio.PDB import MMCIFParser, PDBIO

main_folder = "Main_AF_Folder"
output_folder = os.path.join(main_folder, "Converted_Pdbs")
os.makedirs(output_folder, exist_ok=True)

parser = MMCIFParser(QUIET=True)
io = PDBIO()

def is_model_cif(filename):
    return filename.endswith(".cif") and "summary" not in filename.lower()

for root, dirs, files in os.walk(main_folder):
    for file in files:
        if is_model_cif(file):
            input_path = os.path.join(root, file)
            structure_id = os.path.basename(root)

            try:
                structure = parser.get_structure(structure_id, input_path)

                output_filename = structure_id + ".pdb"
                output_path = os.path.join(output_folder, output_filename)

                io.set_structure(structure)
                io.save(output_path)

                print(f"Converted: {input_path} → {output_filename}")
            except Exception as e:
                print(f"Failed to convert {input_path}: {e}")