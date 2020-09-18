import time
import re
import feedparser


html_braces = re.compile(r"<!-- ([a-z]+) (starts|ends) -->")
other_content = [
    {
        "title": "TALK: Bridge the Gap: Python Data Science and Elasticsearch (EMEA/APAC)",
        "link": "https://www.elastic.co/elasticon/global/agenda?day=day-2&solutionProduct=null&type=null&technicalLevel=null",
        "published": "2020-10-15",
    },
    {
        "title": "TALK: Bridge the Gap: Python Data Science and Elasticsearch (AMER)",
        "link": "https://www.elastic.co/elasticon/global/agenda?day=day-1&solutionProduct=null&type=null&technicalLevel=null",
        "published": "2020-10-14",
    },
    {
        "title": "TALK: Introduction into the Elasticsearch Python Client",
        "link": "https://www.youtube.com/watch?v=UWR9G-U88X0",
        "published": "2020-09-10",
    },
    {
        "title": "INTERVIEW: How urllib3 maintainer Seth Larson streamlined the release process",
        "link": "https://blog.tidelift.com/how-urllib3-maintainer-seth-larson-streamlined-the-release-process",
        "published": "2020-08-18",
    },
    {
        "title": "TALK: Introduction to the Python Elasticsearch Client",
        "link": "https://community.elastic.co/events/details/elastic-emea-virtual-presents-introduction-into-the-python-elasticsearch-client",
        "published": "2020-08-05",
    },
]


def replace_lines(brace_name, lines, replacement):
    replaced_lines = []
    found_start = False
    found_end = False
    for line in lines:
        match = html_braces.match(line.lstrip())
        if match:
            if match.groups() == (brace_name, "starts"):
                found_start = True
                replaced_lines.append(line)
                replaced_lines.extend(replacement)
            elif found_start and match.groups() == (brace_name, "ends"):
                found_end = True
        if found_start == found_end:
            replaced_lines.append(line)
    assert found_start and found_end
    return replaced_lines


def main():
    with open("README.md") as f:
        lines = f.read().split("\n")

    # Reading and updating the blog
    blog_rss = feedparser.parse("https://sethmlarson.dev/feed")
    blog_lines = []
    for entry in blog_rss["entries"]:
        blog_lines.append(
            f"* [{entry['title']}]({entry['link']}) "
            f"{'-'.join(str(x).zfill(2) for x in entry['published_parsed'][:3])}"
        )
    lines = replace_lines("blog", lines, blog_lines)

    # Updating other content
    today = time.gmtime(time.time())[:3]
    other_lines = []
    for entry in sorted(other_content, key=lambda x: x["published"], reverse=True)[-5:]:
        is_upcoming = (
            tuple([int(x.lstrip("0")) for x in entry["published"].split("-")]) > today
        )
        other_lines.append(
            f"* {'**(Upcoming)** ' if is_upcoming else ''}[{entry['title']}]({entry['link']}) {entry['published']}"
        )
    lines = replace_lines("other", lines, other_lines)

    with open("README.md", "w") as f:
        f.write("\n".join(lines).rstrip() + "\n")


if __name__ == "__main__":
    main()
