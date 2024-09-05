# Cyber Threat Intelligence with LLaMA3

## Overview
This project fine-tunes LLaMA 3 7b for Cyber Threat Intelligence (CTI) and evaluates it using [CTIBench](CTIBench%20Paper.pdf)
 .

### Steps:
1. **Data Collection:** Gather CTI data.
2. **Fine-Tuning:** Adapt LLaMA for CTI.
3. **Evaluation:** Test with CTIBench.
4. **Analysis:** Review model performance.



## Setup

1. **Clone & Install:**

    ```bash
    git clone https://github.com/FaroukDaboussi0/Fine-Tuning-LLMs-for-Cyber-Threat-Intelligence.git
    cd CTI_expert
    ```

2. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables:**

    - **Google API Token:** Export your Google API token using the following command:

      ```bash
      export GOOGLE_API_KEY='your_google_api_token'
      ```

    - **Hugging Face Token:** Export your Hugging Face token using the following command:

      ```bash
      export HUGGINGFACE_TOKEN='your_huggingface_token'
      ```


## Usage:
To generate text using the LLaMA 7B model fine-tuned for CTI tasks, use the following code:

```python
from Models.llama_7b_qlora_CTI import generate_text_with_llama_CTI

prompt = "Explain ransomware's impact on security."
generated_text = generate_text_with_llama(prompt)
print(generated_text)
```
[Ask CTI Expert](Ask_cti__expert.ipynb)
## Advanced Usage
**For more advanced usage**, such as training the model with `different configurations` or `upgrading the model`, please refer to the [CTI_Expert.ipynb](CTI_Expert.ipynb) file in Model Fine-Tuning section.

## Open Source Project:
This is an open-source Project. Don’t hesitate to make it better and contribute! We welcome your contributions 🚀

## Datasets Collected

### [CAPEC.csv](Data\collected_data\CAPEC.csv)
- **Description**: Details attack patterns.
- **Columns**: 
    - **ID**: The unique identifier for the attack pattern.
    - **Name**: The name of the attack pattern.
    - **Abstraction**: The level of abstraction of the attack pattern.
    - **Status**: The status of the attack pattern (e.g., draft, published).
    - **Description**: A detailed description of the attack pattern.
    - **Alternate Terms**: Alternative names or synonyms for the attack pattern.
    - **Likelihood Of Attack**: The likelihood of this attack pattern being used.
    - **Typical Severity**: The typical severity of this attack pattern.
    - **Related Attack Patterns**: A list of other attack patterns that are related to this one.
    - **Execution Flow**: A description of the steps involved in carrying out the attack.
    - **Prerequisites**: Any prerequisites that must be met before the attack can be carried out.
    - **Skills Required**: The skills or knowledge required to execute the attack.
    - **Resources Required**: The resources (e.g., tools, software) needed to execute the attack.
    - **Indicators**: Indicators that may be present if this attack is being carried out.
    - **Consequences**: The potential consequences of this attack pattern.
    - **Mitigations**: Steps that can be taken to mitigate the risk of this attack pattern.
    - **Example Instances**: Real-world examples of this attack pattern being used.
    - **Related Weaknesses**: Weaknesses in software or systems that are exploited by this attack pattern.
    - **Taxonomy Mappings**: Mappings to other security taxonomies (e.g., CWE, MITRE ATT&CK).
    - **Notes**: Additional information or notes about the attack pattern.
- **Source**: [CAPEC - MITRE](https://capec.mitre.org)
- **Volume**: 559 distinct CAPECs

### [cve_data.csv](Data\collected_data\cve_data.csv)
- **Description**: Vulnerability data from NVD.
- **Columns**:
    - **CVE_ID**: The unique identifier for the vulnerability.
    - **Description**: A description of the vulnerability.
    - **Date_Published**: The date the vulnerability was published.
    - **CVSS_Vector_String**: The Common Vulnerability Scoring System (CVSS) vector string that represents the vulnerability's severity.
    - **CWE_IDs**: A list of Common Weakness Enumerations (CWE) IDs associated with the vulnerability.
    - **Hyperlinks**: Links to relevant resources, such as the NVD entry.
- **Source**: [National Vulnerability Database (NVD)](https://nvd.nist.gov)
- **Volume**: 73,919 distinct CVEs

### [cwe_data.csv](Data\collected_data\cwe_data.csv)
- **Description**: Details on software weaknesses.
- **Columns**:
    - **ID**: The unique identifier for the software weakness.
    - **Description**: A description of the weakness.
    - **Extended Description**: A more detailed description of the weakness.
    - **References**: Links to related resources, such as the CWE entry.
- **Source**: [CWE - MITRE](https://cwe.mitre.org)
- **Volume**: 857 distinct CWE_IDs

### [Full_attack_patterns_data.json](Data\collected_data\Full_attack_patterns_data.json)
- **Description**: Information on attack techniques.
- **Columns**:
    - **ID**: The unique identifier for the technique.
    - **Technique Name**: The name of the technique.
    - **Description**: A description of how the technique is executed.
    - **Platforms**: The platforms targeted by the technique.
    - **Detection**: Methods for detecting the technique.
    - **Defense Bypassed**: A list of defenses that can be bypassed using the technique.
    - **Kill Chain Phases**: A list of Kill Chain Phases, each containing `kill_chain_name` and `phase_name`.
    - **Related Malwares**: A list of Malwares, each containing `ID`, `Malware Name`, and `comment`.
    - **Related Tools**: A list of Tools, each containing `ID`, `Tool Name`, and `comment`.
    - **Related Intrusion Sets**: A list of Intrusion Sets, each containing `ID`, `intrusion set name`, and `comment`.
    - **Related Campaigns**: A list of Campaigns, each containing `ID`, `Campaign Name`, and `comment`.
    - **Mitigations**: A list of Mitigations, each containing `ID`, `Course of Action Name`, `Description`, and `comment`.
- **Source**: [MITRE ATT&CK](https://attack.mitre.org)
- **Volume**: 780 techniques

### [rapports_data.csv](Data\collected_dataapports_data.csv)
- **Description**:  A collection of threat intelligence reports focusing on cybersecurity groups and their activities. Each report details a specific threat or attack, including the employed techniques, attack patterns, and Indicators of Compromise (IOCs). 
- **Columns**:
    - **link**: A link to the full report.
    - **group_name**: The name of the cybersecurity group responsible for the attack.
    - **rapport**: A summary of the report, detailing the attack's characteristics, including the techniques used, attack patterns observed, and IOCs identified. 
- **Source**: Various cybersecurity sources, including threat intelligence providers and security research organizations.
- **Volume**: 251 reports 




