from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
import re
import pandas as pd
##############
# This file describes a pipeline that automates HADDOCK (docking tool) submission of 
# Aptamer/Proteins for COARSED GRAINED docking, optimized for bioinformatic prediction while following an ab-initio approach; 
###############
PROTEIN_DIR = os.path.join(os.getcwd(), "PROTEIN_DIR")
LIGAND_DIR = os.path.join(os.getcwd(), "LIGAND_DIR")

#Start by defining your login for the HADDOCK platform 
email_cred = 'pg45861@uminho.pt'
pwd_cred = 'Xarreta1@'

def dismiss_cookie_banner(driver):
    for _ in range(3):  # Try up to 3 times
        try:
            got_it_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Got it!")]'))
            )
            driver.execute_script("arguments[0].click();", got_it_button)
            time.sleep(0.5)
            return
        except:
            pass
        try:
            got_it_link = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(text(),"Got it!")]'))
            )
            driver.execute_script("arguments[0].click();", got_it_link)
            time.sleep(0.5)
            return
        except:
            pass
        time.sleep(0.5)

def auto_haddock(driver, protein, ligand, name="Test"):
    #Reloading first page(firstrun only requires login)
    driver.get("https://wenmr.science.uu.nl/haddock2.4/submit/1")
    print("Waiting for first page to load...")
    time.sleep(10)
    dismiss_cookie_banner(driver)
    print(f"Starting Docking - ID: {name}")
    #Defining experiment name based on an external variable c;
    run_name = f'{name}'
    haddock_run = driver.find_element(By.XPATH, '//*[@id="runname"]')
    haddock_run.send_keys(run_name)

    #This page is dynamic, so scrolling towards the general areas is key - defining function
    #Note: Scroll to the element imediatly above the one you aim to find
    def scroll_to(element):
        try:
            js_code = "arguments[0].scrollIntoView();" #Scroll to it
            driver.execute_script(js_code, element) #Scroll to it
        except Exception as e:
            print(f'Failed to scroll into view\n{e}')

    target = driver.find_element(By.XPATH, '//*[@id="p1_pdb_chain"]')
    scroll_to(target)
    time.sleep(5)

    #Sending complete path to file: 
    file01 = driver.find_element(By.XPATH, '//*[@id="p1_pdb_file"]')
    file01.send_keys(protein)

    #Moving to next section:
    target = driver.find_element(By.XPATH, '//*[@id="p2_pdb_chain"]')
    scroll_to(target)
    time.sleep(5)

    #Submitting file 2:
    file02 = driver.find_element(By.XPATH, '//*[@id="p2_pdb_file"]')
    file02.send_keys(ligand)

    #Selecting chemistry
    chemistry = driver.find_element(By.XPATH, '//*[@id="p2_moleculetype"]/option[2]') #Choose "Ligand"
    chemistry.click()

    #Press next
    dismiss_cookie_banner(driver)
    next = driver.find_element(By.XPATH, '//*[@id="submit"]')
    next.click()
    time.sleep(10)

    #Scroll to: 
    try:
        #target = driver.find_element(By.XPATH, '//*[@id="input-params"]/form/div[3]')
        target = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="input-params"]/form/div[3]')))
        scroll_to(target)
        time.sleep(5)

        #Press next: 
        dismiss_cookie_banner(driver)
        next = driver.find_element(By.XPATH, '//*[@id="submit"]')
        next.click()
        time.sleep(5)

        #Defining docking parameters
        #Scroll to: 
        target = driver.find_element(By.XPATH, '//*[@id="collapse1"]/div/div[1]/div/div[1]')
        scroll_to(target)
        time.sleep(5)

        # Disable "Create DNA/RNA restraints?"
        try:
            dna_input = driver.find_element(By.ID, "create_narestraints")
            if dna_input.is_selected():
                driver.execute_script("arguments[0].checked = false; arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", dna_input)
                print("Disabled 'Create DNA/RNA restraints?'")
        except Exception as e:
            print("Could not disable DNA/RNA restraints:", e)
        time.sleep(2)

        # Enable "Random patches"
        try:
            random_input = driver.find_element(By.ID, "ranair")
            if not random_input.is_selected():
                driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", random_input)
                print("Enabled 'Random patches'")
        except Exception as e:
            print("Could not enable Random patches:", e)
        time.sleep(2)

        #Press next:
        dismiss_cookie_banner(driver)
        next = driver.find_element(By.XPATH, '//*[@id="submit"]')
        next.click()
        time.sleep(5)

        #Is research covid related - DEFAULT: NO
        covid = driver.find_element(By.XPATH, '//*[@id="covidConfirmNo"]')
        covid.click()
        time.sleep(10)
    except TimeoutException:
        print(f"Timeout Exception occured - possibly due to PDB formatting issues:\n{TimeoutException}")

    except NoSuchElementException:
        print(f"NoSuchElementException:\n{NoSuchElementException}")

    except Exception as e:
        print(f"An unexpected exception occurred: {e}")

driver = webdriver.Chrome()
driver.get("https://wenmr.science.uu.nl/haddock2.4/submit/1")
print("Waiting for LOGIN page to load...")
dismiss_cookie_banner(driver)
time.sleep(10)

print("Logging in ...")
email = driver.find_element(By.XPATH, '//*[@id="email"]')
pwd = driver.find_element(By.XPATH, '//*[@id="password"]')

email.send_keys(email_cred)
pwd.send_keys(pwd_cred)

pwd.send_keys(Keys.RETURN)

time.sleep(10)
print("Logged in !")
print("Proceed with defining the experiment...")

#File .5 - introduced due to errors on the initial run - related with element loading time
df = pd.read_csv("protein_ligand_mapping.csv") # Insert here a CSV file containing two columns: "PDB_id" and "Aptamer_id", where each column describes protein and aptamer files 
# structures names, respectively
c = 0
for i, r in df.iterrows(): 
    pdb = r["PDB_id"]
    lgd = r["Ligand_id"]
    protein = os.path.join(PROTEIN_DIR, f"{pdb}.pdb") #Here define path to where ALL protein structures are stored; 
    ligand = os.path.join(LIGAND_DIR, f"{lgd}.pdb") #Here define path to where ALL aptamer structures are stored;
    auto_haddock(driver, protein, ligand, lgd) #Very important, apt argument will be the run name
    c += 1 
    if c % 20 == 0:
        print(f"Pause started at: {time.asctime()}") 
        time.sleep(7200) #Wait two hours every 20 entries: this value was obtained by trial and error, due to queuing times accumulating on server
        # A larger pause in between submissions allows for a better queuing organization from the server 
driver.close()