import os
from rdkit import Chem

input_folder = "Pubchem_Ligands"
output_folder = os.path.join(input_folder, "pdb_ligands")

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".sdf"):
        sdf_path = os.path.join(input_folder, filename)
        sdf_supplier = Chem.SDMolSupplier(sdf_path)
        pdb_filename = os.path.splitext(filename)[0] + ".pdb"
        pdb_path = os.path.join(output_folder, pdb_filename)
        with open(pdb_path, "w") as pdb_file:
            for mol in sdf_supplier:
                if mol is not None:
                    pdb_file.write(Chem.MolToPDBBlock(mol))