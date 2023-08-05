With each user
================

The `with_each_user` command is basically nothing but a shortcut/replacement
for constructs like::

    root:~# ls /home | xargs -i su - {} -c "whoami"

That is, its goal is to execute the same command for all users in the system
in a row. The line above can be rewritten with::

    root:~# with_each_user whoami

Additionally, you can filter out unneeded users by their logins, shells and
uid, run commands simultaneously, interactively, and store script outputs
in log files in a separate directory.

See usage for details.


Usage
------


This is the ``with_each_user --help`` output::

    usage: with_each_user [-h] [-m MASK] [-s SHELL] [-u MIN_UID] [-U MAX_UID]
                          [-c CONCURRENCY] [-d CURRENT_DIRECTORY] [-i]
                          [-L LOG_DIRECTORY]
                          command [command ...]

    Execute a command for a number users in the server

    positional arguments:
      command               Shell command to execute

    optional arguments:
      -h, --help            show this help message and exit
      -m MASK, --mask MASK  Filter users by their logins. Globbing is here
                            allowed, you can type, for example, "user*"
      -s SHELL, --shell SHELL
                            Filter users by their shells. For example, you can
                            exclude the majority of system users by issuing
                            "/bin/bash" here
      -u MIN_UID, --min-uid MIN_UID
                            Filter users by their minimal uid.
      -U MAX_UID, --max-uid MAX_UID
                            Filter users by their max uid (to filter out "nobody",
                            for example
      -c CONCURRENCY, --concurrency CONCURRENCY
                            Number of processes to run simultaneously
      -d CURRENT_DIRECTORY, --current-directory CURRENT_DIRECTORY
                            Script working directory (relative to user's home)
      -p, --preserve-environment
                            Preserve root environment. Arguments match the same of
                            "su" command
      -f, --format          Format command line with variables custom for every
                            user. Supported variables: {user}, {uid}, {gid},
                            {home}, {shell}, {gecos}.
      -r, --root            Run command with root privileges (do not "su" to
                            selected user). Option "--format" is helpful there
      -i, --interactive     Interactive execution. Set this flag to run processes
                            interactively
      -L LOG_DIRECTORY, --log-directory LOG_DIRECTORY
                            Directory to store log for all executions. Omit this
                            argument if you want just to print everything to
                            stdout/stderr
