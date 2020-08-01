import time
import re
import feedparser


html_braces = re.compile(r"<!-- ([a-z]+) (starts|ends) -->")
other_content = [
    {
        "title": "TALK: Introduction to the Python Elasticsearch Client",
        "link": "https://community.elastic.co/events/details/elastic-emea-virtual-presents-introduction-into-the-python-elasticsearch-client",
        "published": "2020-08-05",
    },
    {
        "title": "BLOG: Elasticsearch Python client now supports async I/O",
        "link": "https://www.elastic.co/blog/elasticsearch-python-client-now-supports-asyncio",
        "published": "2020-07-15",
    },
    {
        "title": "TALK: Introduction to Eland: Explore and analyze data in Elasticsearch with a Pandas-compatible API",
        "link": "https://www.youtube.com/watch?v=U8fnkzp_sfo",
        "published": "2020-07-10",
    },
    {
        "title": "PROJECT: Eland Demo Jupyter Notebook",
        "link": "https://eland.readthedocs.io/en/latest/examples/introduction_to_eland_webinar.html",
        "published": "2020-07-08",
    },
    {
        "title": "DOCS: Native async support in Elasticsearch Python client",
        "link": "https://elasticsearch-py.readthedocs.io/en/master/async.html",
        "published": "2020-06-18",
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
