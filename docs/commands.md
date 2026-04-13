# Command Reference

> Auto-generated from `lazyjira --help`. Do not edit manually.

## `lazyjira`

```
usage: lazyjira [-h] [--version]
                {issues,comments,move,labels,projects,open,link,query} ...

Zero-dependency CLI for Jira Cloud REST API

positional arguments:
  {issues,comments,move,labels,projects,open,link,query}
                        Available commands
    issues              Issue operations
    comments            Comment operations
    move                Transition issue to a status
    labels              List labels used in a project
    projects            List all Jira projects
    open                Open issue in browser
    link                Link two issues
    query               Run raw JQL query

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

### `lazyjira issues`

```
usage: lazyjira issues [-h]
                       {read,search,list,create,update,status,comment} ...

positional arguments:
  {read,search,list,create,update,status,comment}
    read                Read full issue details
    search              Search issues via JQL
    list                List issues (table or JSON)
    create              Create a new issue
    update              Update an issue
    status              Transition issue status
    comment             Add a comment

options:
  -h, --help            show this help message and exit
```

### `lazyjira issues list`

```
usage: lazyjira issues list [-h] [--project PROJECT] [--status STATUS]
                            [--status-ne STATUS_NE] [--status-in STATUS_IN]
                            [--status-nin STATUS_NIN] [--label LABEL]
                            [--assignee ASSIGNEE] [--priority PRIORITY]
                            [--limit LIMIT] [--plain] [--order ORDER]

options:
  -h, --help            show this help message and exit
  --project, -p PROJECT
                        Project key
  --status, -s STATUS   Filter by status
  --status-ne STATUS_NE
                        Exclude status (not equal)
  --status-in STATUS_IN
                        Filter by statuses (comma-separated)
  --status-nin STATUS_NIN
                        Exclude statuses (comma-separated)
  --label, -l LABEL     Filter by label
  --assignee, -a ASSIGNEE
                        Filter by assignee
  --priority PRIORITY   Filter by priority
  --limit LIMIT         Max results
  --plain               Plain JSON output
  --order ORDER         JQL ORDER BY clause
```

### `lazyjira issues create`

```
usage: lazyjira issues create [-h] [-d DESCRIPTION] [--project PROJECT]
                              [--status STATUS] [--priority PRIORITY]
                              [--labels LABELS [LABELS ...]] [--type TYPE]
                              [--assignee ASSIGNEE] [--parent PARENT]
                              [--duedate DUEDATE]
                              title

positional arguments:
  title                 Issue summary/title

options:
  -h, --help            show this help message and exit
  -d, --description DESCRIPTION
                        Issue description (markdown)
  --project, -p PROJECT
                        Project key
  --status, -s STATUS   Initial status (transitions after creation)
  --priority PRIORITY   Priority (1=Highest, 4=Low)
  --labels, -l LABELS [LABELS ...]
                        Labels
  --type, -t TYPE       Issue type (auto-detected if omitted)
  --assignee ASSIGNEE   Assignee account ID
  --parent PARENT       Parent issue key
  --duedate DUEDATE     Due date (YYYY-MM-DD)
```

### `lazyjira issues search`

```
usage: lazyjira issues search [-h] [--project PROJECT] [--status STATUS]
                              [--status-ne STATUS_NE] [--status-in STATUS_IN]
                              [--status-nin STATUS_NIN] [--label LABEL]
                              [--assignee ASSIGNEE] [--priority PRIORITY]
                              [--order ORDER] [--limit LIMIT]
                              [--update-cache FILE]
                              [query]

positional arguments:
  query                 Text search query

options:
  -h, --help            show this help message and exit
  --project, -p PROJECT
                        Project key
  --status, -s STATUS   Filter by status
  --status-ne STATUS_NE
                        Exclude status (not equal)
  --status-in STATUS_IN
                        Filter by statuses (comma-separated)
  --status-nin STATUS_NIN
                        Exclude statuses (comma-separated)
  --label, -l LABEL     Filter by label
  --assignee, -a ASSIGNEE
                        Filter by assignee
  --priority PRIORITY   Filter by priority (1-4)
  --order ORDER         JQL ORDER BY clause
  --limit LIMIT         Max results (default: 50)
  --update-cache FILE   Write results to cache file
```

### `lazyjira issues read`

```
usage: lazyjira issues read [-h] key

positional arguments:
  key         Issue key (e.g. PROJ-123)

options:
  -h, --help  show this help message and exit
```

### `lazyjira issues update`

```
usage: lazyjira issues update [-h] [--status STATUS] [--summary SUMMARY]
                              [--priority PRIORITY]
                              [--description DESCRIPTION]
                              [--labels-add LABELS_ADD [LABELS_ADD ...]]
                              [--labels-remove LABELS_REMOVE [LABELS_REMOVE ...]]
                              key

positional arguments:
  key                   Issue key

options:
  -h, --help            show this help message and exit
  --status, -s STATUS   Transition to status
  --summary SUMMARY     Update summary
  --priority PRIORITY   Priority (1=Highest, 4=Low)
  --description, -d DESCRIPTION
                        Update description (markdown)
  --labels-add LABELS_ADD [LABELS_ADD ...]
                        Add labels
  --labels-remove LABELS_REMOVE [LABELS_REMOVE ...]
                        Remove labels
```

### `lazyjira comments`

```
usage: lazyjira comments [-h] {create,add,list} ...

positional arguments:
  {create,add,list}
    create           Add a comment
    add              Add a comment (alias)
    list             List comments

options:
  -h, --help         show this help message and exit
```

### `lazyjira comments create`

```
usage: lazyjira comments create [-h] --body BODY key

positional arguments:
  key              Issue key

options:
  -h, --help       show this help message and exit
  --body, -b BODY  Comment text
```

### `lazyjira comments list`

```
usage: lazyjira comments list [-h] key

positional arguments:
  key         Issue key

options:
  -h, --help  show this help message and exit
```

### `lazyjira move`

```
usage: lazyjira move [-h] key status

positional arguments:
  key         Issue key
  status      Target status name

options:
  -h, --help  show this help message and exit
```

### `lazyjira labels`

```
usage: lazyjira labels [-h] [--project PROJECT]

options:
  -h, --help            show this help message and exit
  --project, -p PROJECT
                        Project key
```

### `lazyjira projects`

```
usage: lazyjira projects [-h]

options:
  -h, --help  show this help message and exit
```

### `lazyjira open`

```
usage: lazyjira open [-h] key

positional arguments:
  key         Issue key

options:
  -h, --help  show this help message and exit
```

### `lazyjira link`

```
usage: lazyjira link [-h] [--type TYPE] inward outward

positional arguments:
  inward           Inward issue key
  outward          Outward issue key

options:
  -h, --help       show this help message and exit
  --type, -t TYPE  Link type (default: Blocks)
```

### `lazyjira query`

```
usage: lazyjira query [-h] [--fields FIELDS] [--limit LIMIT] jql

positional arguments:
  jql                  JQL query string

options:
  -h, --help           show this help message and exit
  --fields, -f FIELDS  Comma-separated field names
  --limit LIMIT        Max results
```

---

*Generated by `scripts/generate_docs.py`*
