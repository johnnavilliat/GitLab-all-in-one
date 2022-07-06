#This script will take all high and critical issues within a project and create a single Gitlab issue

import requests
import json
import gitlab

#Snyk Parameters
snyk_org_id="xxxxxx"
snyk_project_id="xxxxxx"
snyk_token="xxxxxx"
snyk_headers = {
  'Authorization': 'token '+snyk_token,
  'Content-Type': 'application/json'
}

#GitLab Parameters
gitlab_token="xxxxxx"
gitlab_project_id = "xxxxxx"

#Pull in project info from Snyk
snyk_url="https://snyk.io/api/v1/org/"+snyk_org_id+"/project/"+snyk_project_id
snyk_body={}

response = requests.request("GET", snyk_url, headers=snyk_headers, data=snyk_body)
response_dict = response.json()
crit_count=str((response_dict['issueCountsBySeverity']['critical']))
proj_name=response_dict['name']
proj_link=response_dict['browseUrl']

#Pull in list of critical issues from the project
snyk_url="https://snyk.io/api/v1/org/"+snyk_org_id+"/project/"+snyk_project_id+"/aggregated-issues"

snyk_body= json.dumps({
  "includeDescription": False,
  "includeIntroducedThrough": False,
  "filters": {
    "severities": [
      "critical"
    ],
    "exploitMaturity": [
      "mature",
      "proof-of-concept",
      "no-known-exploit",
      "no-data"
    ],
    "types": [
      "vuln",
      "license"
    ],
    "ignored": False,
    "patched": False,
    "priority": {
      "score": {
        "min": 0,
        "max": 1000
      }
    }
  }
})

response = requests.request("POST", snyk_url, headers=snyk_headers, data=snyk_body)
response_dict = response.json()


gl = gitlab.Gitlab('https://gitlab.com', private_token=gitlab_token)
p = gl.projects.get(gitlab_project_id)

#Creating the payload for the GitLab Issue

payload = {'title': proj_name+" - "+crit_count+" Critical Vulnerabilities",
          'description': "There are currently "+crit_count+" Critical Vulnerabilities in your project. "
                         "Click <a href=" + proj_link +">here</a> to access the project." + "<br>"
           }

desc_count=1

while response_dict['issues']:
    issue = response_dict['issues'].pop()
    payload['description'] += "<br>"
    payload['description'] += "<b>" + issue['pkgName']+" - "+issue['issueData']['title'] + "</b>" + "<br>"
    payload['description'] += "\nCVSS Score: "+str(issue['issueData']['cvssScore']) + "<br>"
    payload['description'] += "\nMaturity: "+issue['priority']['factors'][0]['description'] + "<br>"
    payload['description'] += "\n<a href=" + issue['issueData']['url'] +">More info</a>" + "<br>"

desc_count+=1

p.issues.create(payload)
