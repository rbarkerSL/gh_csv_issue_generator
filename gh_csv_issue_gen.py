import argparse
import sys

def parse_csv(csv:str) -> list[str]:
    repos:list[str] = []
    with open(csv,"r") as infile:
        for line in infile.readlines():
            repos.append(line.strip().replace(",","/"))
    return repos

def gen_issue_script(template:str, title:str, repo_list:list[str]):
    from datetime import datetime
    from os import chmod

    print("Generating the Issue Gen shell script")

    command:str = "gh issue create --repo [REPO] --title \"" + title + "\" --body-file " + template
    
    cmd_list:list[str] = []

    try:
        for repo in repo_list:
            cmd:str = command.replace("[REPO]",repo)
            cmd_list.append(cmd)
        
        issue_script:str = "issue_gen.sh"
        with open(issue_script, "w") as script:
            for line in cmd_list:
                line += "\n"
                print(line)
                script.write(line)
                script.write("sleep 2\n") # need sleep 2 for gh api to be happy

        print("Generation complete. chmod to 755 to enable execution of the script")
        chmod(issue_script,0o755)
    
    except Exception as e:
        raise e

    print("Complete.")

def parse_audit_args() -> tuple[str,str]:
    from os.path import exists as path_exists # just need to check if os.path.exists() returns true for the audit file

    parser = argparse.ArgumentParser(description="Generate a script that will create several github issues across the repositories in the specified audit_list.")
    parser.add_argument("-c","--csv-file",dest="csv_file",type=str,help="The csv file which specifies all required repositories for the template issue")
    parser.add_argument("-i","--issue-template",dest="issue_template",type=str,help="The template file for the issue generator script")
    parser.add_argument("-t","--title",dest="title",type=str,help="The title for the generated issue")
    args = parser.parse_args()

    if args.csv_file is None or args.csv_file == "":
        raise RuntimeError("No csv_file specified")
    
    if not path_exists(args.csv_file):
        raise RuntimeError("The specified csv_file does not exist or is not valid")
    
    if args.issue_template is None or args.issue_template == "":
        raise RuntimeError("No issue_template specified")
    
    if not path_exists(args.issue_template):
        raise RuntimeError("The specified issue_template does not exist or is not valid")
    
    if args.title == None:
        raise RuntimeError("Must specify the title for the issue")
    
    return args.csv_file, args.issue_template, args.title

def main():
    try:
        csv_name:str = ""
        issue_template:str = ""
        title:str = ""
        csv_name, issue_template, title = parse_audit_args()
        repo_list:list[str] = parse_csv(csv=csv_name)
        print("Issue Template: ", issue_template, "\tCSV file:", csv_name, "\tIssue title:", title)
        gen_issue_script(template=issue_template,title=title,repo_list=repo_list)

    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
    sys.exit(0) # clean execution exit happily
