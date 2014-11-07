#!/usr/bin/env python

class Mysql:

    def __init__ (self, database, username, password=None):
        """Initialize.

        database The database name.
        username The database username.
        password The password to use. This argument is optional.
        """

        self.database = database
        self.username = username
        self.password = password

        self.mysql_command = [ "mysql", "-u", self.username ]
        if self.password:
            self.mysql_command += [ "--password=%s" % (self.password) ]

    def query (self, query):
        """Query the database.

        query The query command to run.

        The function returns a list of strings with the output of the query.
        """

        import subprocess
        import sys

        mysql = subprocess.Popen(self.mysql_command, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        mysql.stdin.write(string_io_wrap("use %s;\n" % (self.database)))
        mysql.stdin.write(string_io_wrap(query))

        stdoutdata, stderrdata = mysql.communicate()

        if sys.version_info.major == 3:
            stdoutdata = stdoutdata.decode("UTF-8")

        stdoutdata = stdoutdata.splitlines()
        stdoutdata.pop(0)

        if mysql.returncode != 0:
            for i in stdoutdata:
                print(i.rstrip())
            raise Exception("failed to query database")

        return stdoutdata

    def get_all_revisions (self):
        """Retrieve all revisions on all pages. Only pages in the main and
        user namespaces are considered.

        This function returns a list of all edits, ordered by timestamp. Each
        list element contains a dictionary of { timestamp, page_id, page_name,
        username, user_email, mediawiki_text, markdown_text }.
        """

        result = self.query("select concat_ws(',', "
                + "revision.rev_timestamp, "
                + "revision.rev_page, "
                + "revision.rev_deleted, "
                + "page.page_title, "
                + "user.user_real_name, "
                + "user.user_email, "
                + "text.old_text) "
                + "from revision "
                + "inner join text on text.old_id = revision.rev_text_id "
                + "inner join page on page.page_id = revision.rev_page "
                + "inner join user on "
                + "user.user_id = (select if(revision.rev_user = 0, 1, revision.rev_user)) "
                + "order by revision.rev_timestamp")

        print("got %s revisions" % (len(result)))

        revisions = []
        for i in result:
            temp = i.split(",", 6)
            temp[6] = temp[6].split("\\n")
            try:
                temp.append(mediawiki_to_markdown(temp[6]))
            except Exception as e:
                print("can not convert mediawiki text "
                        + ("for page %s, " % (temp[2]))
                        + "storing original mediawiki text")
                temp.append(temp[6])
            if int(temp[2]) != 0:
                deleted = True
            else:
                deleted = False
            revisions.append({"timestamp":temp[0], "page_id":int(temp[1]),
                "deleted":deleted, "page_name":temp[3], "username":temp[4],
                "user_email":temp[5], "mediawiki_text":temp[6],
                "markdown_text":temp[7]})

        return revisions

def string_io_wrap (string):
    """Properly treat strings across python2/3 for IO operations
    (file.write()).

    This function returns a proper string.
    """

    import sys

    if sys.version_info.major == 3:
        string = bytes(string, "UTF-8")

    return string

def mediawiki_to_markdown (page_text):
    """Convert a text blob from mediawiki format to markdown.

    This function returns the converted text as a list of strings.
    """

    import subprocess
    import sys

    pandoc_cmd = [ "pandoc", "--from", "mediawiki", "--to", "markdown_github",
            "--base-header-level", "2" ]

    pandoc = subprocess.Popen(pandoc_cmd, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=False)
    for i in page_text:
        pandoc.stdin.write(string_io_wrap(i + "\n"))

    stdoutdata, stderrdata = pandoc.communicate()

    if sys.version_info.major == 3:
        stdoutdata = stdoutdata.decode("UTF-8")
        stderrdata = stderrdata.decode("UTF-8")

    stdoutdata = stdoutdata.splitlines()
    stderrdata = stderrdata.splitlines()

    if pandoc.returncode != 0:
        raise Exception("failed to convert mediawiki page")

    return stdoutdata

def convert_wiki_date (wiki_timestamp):
    """Convert a wiki timestamp to a git datestring.

    The format of timestamps used in MediaWiki URLs and in some of the
    MediaWiki database fields is yyyymmddhhmmss. For example, the timestamp
    for August 9th, 2010 00:30:06 UTC is 20100809003006. The timezone for
    these timestamps is UTC.
    """

    return (wiki_timestamp[0:4] + "-" + wiki_timestamp[4:6] + "-" +
            wiki_timestamp[6:8] + "T" + wiki_timestamp[8:10] + ":" +
            wiki_timestamp[10:12] + ":" + wiki_timestamp[12:14])

def main ():
    """
    The main function.
    """

    import argparse
    import os
    import re
    import subprocess
    import sys

    parser = argparse.ArgumentParser(description="This script converts the "
            + "pages of a mediawiki database (using mysql) into markdown "
            + "format, preserving the editing history and attribution. The "
            + "converted pages are stored in a git repository.")

    parser.add_argument("--database",
            help = "The mysql database",
            required = True)

    parser.add_argument("--user",
            help = "The mysql database user",
            required = True)

    parser.add_argument("--password",
            help = "The mysql database password")

    parser.add_argument("--output-dir",
            help = "The path of the resulting converted pages",
            default = "pages")

    options = parser.parse_args()

    mysql = Mysql(options.database, options.user, options.password)

    revisions = mysql.get_all_revisions()

    if os.path.exists(options.output_dir):
        raise Exception("The output path '%s' already exists" % ("pages"))

    os.mkdir(options.output_dir)

    git = subprocess.Popen(["git", "init"], cwd=options.output_dir)
    git.wait()

    for rev in revisions:
        filename = rev["page_name"] + ".md"

        if rev["deleted"]:
            git = subprocess.Popen(["git", "rm", filename],
                    cwd=options.output_dir)
            git.wait()
        else:
            new_page = open(os.path.join("./pages", filename), "w")
            new_page.write("---\n")
            new_page.write("layout: default\n")
            new_page.write("title: %s\n" % (re.sub("_", " ", rev["page_name"])))
            new_page.write("---\n")
            new_page.write("\n")

            for i in rev["markdown_text"]:
                new_page.write(i + "\n")
            new_page.close()

            git = subprocess.Popen(["git", "add", filename],
                    cwd=options.output_dir)
            git.wait()

        datestring = convert_wiki_date(rev["timestamp"])

        git = subprocess.Popen(["git", "commit", "--author", "\"%s <%s>\"" %
            (rev["username"], rev["user_email"]), "--date", datestring, "-m",
            "Updating %s" % (rev["page_name"])],
            cwd=options.output_dir)
        git.wait()

if __name__ == "__main__":
    main()
