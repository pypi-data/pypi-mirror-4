__version__ = "0.0.1-develop-9-g687e309"
__git_commiter_name__ = "Guy Rozendorn"
__git_commiter_email__ = "guy@rzn.co.il"
__git_branch__ = 'develop'
__git_remote_tracking_branch__ = 'origin/develop'
__git_remote_url__ = 'git@gitserver:host/infi-jira-cli.git'
__git_head_hash__ = '687e3098620c41ad023c6e18612ca0fdd2aec24a'
__git_head_subject__ = 'HOSTDEV-553 jissue resolve --commit=<commit>'
__git_head_message__ = ''
__git_dirty_diff__ = 'diff --git a/src/infi/jira_cli/__init__.py b/src/infi/jira_cli/__init__.py\nindex 345b624..4fb52ae 100644\n--- a/src/infi/jira_cli/__init__.py\n+++ b/src/infi/jira_cli/__init__.py\n@@ -18,7 +18,7 @@ Options:\n     --resolve-as=<resolution>    resolution string [default: Fixed]\n     --issue-type=<issue-type>    issue type string [default: Bug]\n     --link-type=<link-type>      link type string [default: Duplicate]\n-    --commit=<commit>            deduce issue and message from commit\n+    --commit=<commit>            deduce issue and message from git commit\n     --help                       show this screen\n \n More Information:\n'