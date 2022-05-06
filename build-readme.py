import json
import re
import feedparser
import urllib3
from dateutil import parser


html_braces = re.compile(r"<!-- ([a-z]+) (starts|ends) -->")
http = urllib3.PoolManager()
pypi_projects = [
    "urllib3",
    "elastic-enterprise-search",
    "elasticsearch7",
    "elasticsearch",
    "ecs-logging",
    "psl",
    "eland",
    "pyvbox",
    "virtualbox",
    "elastic-transport",
    "hstspreload",
    "sniffio",
    "unasync",
    "elastic-cloud",
    "h2",
    "elasticsearch7-dsl",
    "elasticsearch-dsl",
    "elastic-app-search",
    "selectors2",
    "elasticsearch6-dsl",
    "elasticsearch8-dsl",
    "elasticsearch8",
    "elasticsearch9",
    "elasticsearch9-dsl",
    "socksio",
    "rfc3986",
    "elasticsearch-dsl-async",
    "elasticsearch-async",
    "trustme-cli",
    "irl",
    "win-inet-pton",
    "whatwg-url",
    "brotlipy",
    "brotlicffi",
    "requests",
    "distro",
    "truststore",
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


def get_latest_pypi_releases():
    releases = []
    for project in pypi_projects:
        resp = http.request("GET", f"https://pypi.org/pypi/{project}/json")
        if resp.status == 200:
            data = json.loads(resp.data.decode("utf-8"))
            for version, release in data["releases"].items():
                try:
                    uploaded_at = max([parser.parse(x["upload_time_iso_8601"]) for x in release])
                    releases.append((f"{project}-{version}", uploaded_at, f"https://pypi.org/project/{project}/{version}"))
                except ValueError:
                    continue

    return [{"title": r[0], "published": str(r[1].date()), "link": r[2]} for r in sorted(releases, key=lambda x: x[1], reverse=True)][:10]


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
    release_lines = []
    releases = get_latest_pypi_releases()
    for entry in releases:
        release_lines.append(
            f"* [{entry['title']}]({entry['link']}) {entry['published']}"
        )
    lines = replace_lines("other", lines, release_lines)

    with open("README.md", "w") as f:
        f.write("\n".join(lines).rstrip() + "\n")


if __name__ == "__main__":
    main()
