# IDinsight-Indus Action POWER Project

## Objective
Build a data system that helps Indus Action target beneficiaries for certain benefits contingent on other benefits they are eligible for or have claimed already.

## Detailed Proposal
The focus is on proposals #5 and #6 following [discussion](https://docs.google.com/document/d/1Q-YMbRrrZ715-hJ8NDbOjx5tRWdgrjtc03N8OLHP4wE/edit#) with Indus Action:

### Proposal 5
Identify individuals that are likely eligible for BoCW claims so that Indus Action can contact them through awareness campaigns; starting with BoCW, Delhi.

### Proposal 6
Identify different benefits that beneficiaries of RTE are eligible for so Indus Action can target future activities to get similar beneficiaries to apply for different benefits.
Benefits to start with:
- MGNREGA
- PM Kisan Samman Yojana
- Ujjwala Yojana
- Jan Dhan account holder (DBT)
- Old age / Widow / Disability Pension
- Registered Labour/ Construction worker
- BPL Ration Card
- General Ration Card
- Maternity benefits

## First run setup
1. Cloning this repository
2. Run `make directories` if you have `make` installed else create a `data`  and `logs` folder
3. Create the following symbolic links within `data`
   (See Ways of [Working Appendix A](https://docs.google.com/document/d/118Bw155iqn9x7PQ25TlkH8FqKH8aHFidGYp3d0nD7k4/edit#heading=h.nuhdqpgbwoxd) or [this youtube video](https://www.youtube.com/watch?v=43mGItOoJIM))

| Source (link name) | Target (actual file name) |
|----|----|
| 00_raw | Dropbox (IDinsight)\Indus Action\2. Workstreams\3. Data Science and Systems\00_raw |
| 01_preprocessed | Dropbox (IDinsight)\Indus Action\2. Workstreams\3. Data Science and Systems\01_preprocessed |

### Other folders to create in `data` (not linked symbolically)
- 02_modelinput
- 03_intermediate
- 04_modeloutput
- 99_temp

## Note
** Do not commit secrets to Git ** 

## GCP
You need to have an environment variable for BigQuery

MAC/Linux:  export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"

Window (cmd prompt): set GOOGLE_APPLICATION_CREDENTIALS=[PATH] 

Where [PATH]is the full path to the directory. 
TIP: If you use conda, you can set this automatically when you activate the environment. See [here](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#saving-environment-variables) for more details.

## Datasets
Pulled from GCP:
- All beneficiaries Indus Action has helped
- Squadron allotment
- Corona calling

Find them in Boxcrypted DropBox (Indus Action > 2. Workstreams > 3. Data Science and Systems)





