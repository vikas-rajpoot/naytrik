
TAX_COUNTY_PROMPT = """
**Objective:**
Flexibly navigate diverse tax websites to find and view parcel details for {parcel_number} for a given {state} and {county}, and then locate the tax/payment information. This prompt is designed to handle both single and split-box parcel number inputs.

**Core Principles:**
- **Adaptability:** Assume websites vary. Adapt to different layouts, labels, and multi-step workflows.
- **Resilience:** Handle common web obstacles like pop-ups, varied navigation, and search result formats.
- **State-Change Verification:** After performing an action (like a click), verify that the page state has changed. If it hasn't, retry the action once.
- **Site Constraint**: Remain on the provided website domain. Do not navigate to external sites like Google to find information.
- **CAPTCHA Handling**: If a CAPTCHA is encountered at any point, stop immediately and mark the task as complete.
- **Failure Condition**: If tax information cannot be located after following all relevant steps, conclude the task with a "not found" status.
- **No Results Found**: If a search yields no results for the given parcel number, the task is considered complete. Do not attempt further searches or navigation.

**Workflow Steps:**

1.  **Navigate to Search Portal (If Necessary):**
   - **Goal:** Reach the property search form from the landing page.
   - **Condition:** Perform this step only if the initial page does not contain a search form.
   - **Actions:**
      - Scan the page for navigation elements like menus, buttons, or links with keywords such as "Search," "Property," "Tax," "Property Info", "Pay Property Tax",  "Real Property Tax", "PAY NOW (BUTTON)" "Parcel,", "MAP Number", "Tax Map", "Assessments" or similar terminology ."
      - This may be a multi-step process. you may need to click on buttons multiple time. 
      - Continue clicking through relevant links until you arrive at a page containing the search form (i.e., a page with input fields for parcel number, address, etc.).
   - **Note:** If the initial page is already the search form/portal, then don't try to access any link. completely skip this step and proceed to step 2, and also don't do more then 5 action/steps to complete this step.
   
2.  **Prepare the Search Form:**
   - **Goal:** Make the search form accessible and ready for input.
   - **Actions:** Wait for the page to load. Dismiss any initial overlays, disclaimers, or cookie banners by clicking "Accept," "Agree," "OK," or a close icon ('X'). This might be a multi-step process if there are several modals.

3.  **Configure Search Criteria:**
   - **Goal:** Correctly set all required fields before searching.
   - **Actions:**
    - **State Selection:** If a state selector is present and `{state}` is not 'None', select `{state}`.
    - **County Selection:** If a county selector is present and `{county}` is not 'None', select `{county}`.
    - **Search Type:** If a choice is offered (e.g., "By Parcel," "By Owner", "Choose Collection" etc), 
         select the option for "Parcel Number," "Account ID,", "Town & County {search_year}", "Tax" or a similar identifier.
    - **Year Selection:** If a tax year selector is present, set it to `{search_year}`. After selecting the year, look for and click any continuation buttons like "Continue," "Go," "Submit," or "Next" to proceed to the search form page.
    - **Parcel Input:** Locate the input field(s) for the parcel number (e.g., "Parcel Number," "Account Number," "Property ID," "MAP NUMBER"). click exactly one the input box [____], locate properly. 
        - **Single Field:** If it's a single input field, enter the full `{parcel_number}`.
        - **Multiple Fields:**
         - **Scenario A: Nothing specify in parcel number:** If the input is split into several boxes, split `{parcel_number}` by its delimiter (e.g., '-', ' ') and enter each part into the corresponding box. 
               For example, if the parcel is "12-345-678" and there are three boxes, enter "12" in the first, "345" in the second, and "678" in the third.
         - **Scenario B: Identifier specified in the parcel number** like "parcel_number": "BLOCK 3019 LOT 15", then use the BLOCK AND LOT and input the numbers 3019 in BLOCK and 15 in LOT.
         
    - **Self-Correction:** If any selection (like year or search type) clears other fields, re-enter the necessary information. Ensure all required fields are correctly populated before proceeding.

4.  **Execute Search:**
   - **Goal:** Trigger the search and wait for results.
   - **Actions:** Click the "Search" or "Submit" button. If that fails or is not available, press the 'Enter' key in the parcel number input field as an alternative. Wait for the results to load.

5.  **Process Search Outcome:**
   - **Goal:** Navigate from the search outcome to the specific parcel's tax information.
   - **Scenario A: List of Results:** If the search displays a list of results, scan for an exact match of `{parcel_number}`. Click the corresponding link or button (e.g., "View Details," "Select," or the parcel number itself) to open the details page.
   - **Scenario B: Direct to Details:** If the search leads directly to a parcel details page, this step is complete.
   - **Scenario C: Partial page of Details:** If the search leads directly to a parcel details page, but tax info is not there try to scroll down and locate.
   - **Scenario D: No Results:** If no results are found, the task is complete with a "not found" status. Mark Task as complete no need to do anything.

6.  **Locate Tax Information:**
   - **Goal:** From the parcel details page, find the section or page with tax payment information.
   - **Actions:** First, check if tax information (like "Amount Due", "Total Tax", "Taxes Payable",, ) is already visible on the current page. If it is, this step is complete. 
     If not, look for and click on links, tabs, or buttons labeled "Taxes", "Tax Statement" "Property Tax Information", "Property Taxes Due"
     "Tax Bill", "Tax INFO", "Payments", "Amount Due", "Payable", "Billing",  
     or similar terms to navigate to the tax information page. This may require navigating through one or more pages.

7.  **Confirm and Finalize:**
   - **Goal:** Verify that the page containing tax due information is displayed.
   - **Actions:** Wait for the tax/payment page to load. Once a page containing terms like "Amount Due", "Base Amount",  "Total Tax", "Taxes Payable", or similar financial details for the correct parcel is visible, 
   the task is successfully completed. Do not perform any further actions.

"""


