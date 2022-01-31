# notion-tools

My personal tools for automation Notion workflows.

# setup

1. Install [pdm](https://pdm.fming.dev/).
2. Clone the repo.
3. Configure [keyring](https://pypi.org/.project/keyring/).
4. `cd notion-tools`.
5. `pdm install`.
6. Install the script `pip install --editable src`

# Run the tools

```console
$ weekly_readings --help
Usage: weekly_readings [OPTIONS]

Options:
 --count INTEGER       Number of articles to select  [default: 7]
 -t, --add-to-todoist  Add articles to Todoist  [default: False]
 --due INTEGER         Due after how many days.  [default: 7]
 -c, --checklist       Print formatted checklist which is pastbale into
                       notion with backlinks.  [default: True]
 --help                Show this message and exit

$ capture --help
Usage: capture [OPTIONS]

  Capture a todo/idea quickly into notion

Options:
  --help  Show this message and exit.


```
