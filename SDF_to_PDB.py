import rdkit
from rdkit import Chem
from rdkit.Chem import AllChem

# Load the SDF file
sdf_file = "PubChem_polyethylene_terephthalate_Conformer3D_COMPOUND_CID_18721140.sdf"
sdf_supplier = Chem.SDMolSupplier(sdf_file)

# Write to PDB
output_pdb = "PET.pdb"
with open(output_pdb, "w") as pdb_file:
    for mol in sdf_supplier:
        if mol is not None:
            pdb_file.write(Chem.MolToPDBBlock(mol))