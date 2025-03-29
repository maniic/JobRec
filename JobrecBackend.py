"""
JobrecBackend.py

This module implements the backend logic for the JobRec recommendation system.
It includes:
- A weighted bipartite graph structure to model relationships between skills and jobs.
- Live job fetching from the Findwork API.
- A matching algorithm to recommend jobs based on a user’s skills.
- Console-based interaction (optional for testing/debugging).

Functions include loading API keys, building the graph, and ranking jobs by relevance.
"""
import os
from typing import Any, Union
import requests
from dotenv import load_dotenv
import python_ta


class _WeightedVertex:
    """
    A vertex in a weighted bipartite graph, representing either a skill or a job.

    Attributes:
        - item: The name of the skill or job.
        - kind: Either 'skill' or 'job'.
        - neighbours: A dictionary of neighboring vertices with their edge weights.
    """
    item: Any
    kind: str
    neighbours: dict['_WeightedVertex', Union[int, float]]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind."""
        self.item = item
        self.kind = kind
        self.neighbours = {}


class WeightedGraph:
    """
    A weighted undirected bipartite graph connecting skills to job postings.

    Vertices are categorized by kind ('skill' or 'job') and edges between them
    represent the relevance of a skill to a job, with weights indicating frequency.
    """
    _vertices: dict[Any, '_WeightedVertex']

    def __init__(self) -> None:
        """Initialize an empty weighted graph."""
        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to the graph.

        >>> g = WeightedGraph()
        >>> g.add_vertex("python", "skill")
        >>> "python" in g._vertices
        True
        """
        if item not in self._vertices:
            self._vertices[item] = _WeightedVertex(item, kind)

    def add_edge(self, item1: Any, item2: Any, weight: Union[int, float] = 1) -> None:
        """Add an undirected edge with weight between item1 and item2.

        >>> g = WeightedGraph()
        >>> g.add_vertex("python", "skill")
        >>> g.add_vertex("Job A", "job")
        >>> g.add_edge("python", "Job A", weight=3)
        >>> g.get_weight("python", "Job A")
        3
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight
        else:
            raise ValueError

    def get_weight(self, item1: Any, item2: Any) -> Union[int, float]:
        """Return the weight between two connected vertices.

        >>> g = WeightedGraph()
        >>> g.add_vertex("skill", "skill")
        >>> g.add_vertex("job", "job")
        >>> g.add_edge("skill", "job", 2)
        >>> g.get_weight("skill", "job")
        2
        """
        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        return v1.neighbours.get(v2, 0)

    def get_all_vertices(self, kind: str = '') -> set:
        """Return all vertex items, optionally filtered by kind.

        >>> g = WeightedGraph()
        >>> g.add_vertex("python", "skill")
        >>> g.add_vertex("java", "skill")
        >>> g.add_vertex("Data Scientist", "job")
        >>> g.get_all_vertices("skill") == {"python", "java"}
        True
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def has_vertex_helper(self, item: str) -> bool:
        """Return whether the given item exists as a vertex in the graph."""
        return item in self._vertices


def load_api_key() -> str:
    """Load the Findwork API key from the .env file.

    >>> isinstance(load_api_key(), str)
    True
    """
    load_dotenv()
    return os.getenv("FINDWORK_API_KEY")


def fetch_jobs(query: str, api_key: str, limit: int = 20) -> list[dict]:
    """Fetch job listings from the Findwork API using the given query.

    >>> jobs = fetch_jobs("python", "invalid_key", 1)
    Error fetching jobs: 401
    >>> isinstance(jobs, list)
    True
    """
    url = "https://findwork.dev/api/jobs/"
    headers = {"Authorization": f"Token {api_key}"}
    params = {"search": query, "limit": limit}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Error fetching jobs: {response.status_code}")
        return []


def build_graph(skills: list[str], jobs: list[dict]) -> WeightedGraph:
    """Build a weighted bipartite graph connecting skills to job listings.

    >>> g = build_graph(["python"], [{"role": "Developer", "company_name": "ABC", "description": "Looking for Python dev", "text": ""}])
    >>> len(g.get_all_vertices("job")) > 0
    True
    """
    graph = WeightedGraph()

    for skill in skills:
        graph.add_vertex(skill.lower(), "skill")

    for job in jobs:
        job_id = f"{job['role']} at {job['company_name']}"
        graph.add_vertex(job_id, "job")

        content = (job.get("text", "") + " " + job.get("description", "")).lower()
        match_score = 0
        for skill in skills:
            count = content.count(skill.lower())
            if count > 0:
                graph.add_edge(skill.lower(), job_id, weight=count)
                match_score += count

        # Ensure at least one connection so user always sees results
        if match_score == 0 and skills:
            fallback_job_id = job_id + " [Low Match]"
            graph.add_vertex(fallback_job_id, "job")
            graph.add_edge(skills[0].lower(), fallback_job_id, weight=1)

    return graph


def recommend_jobs(graph: WeightedGraph, skills: list[str], limit: int = 5) -> list[tuple[str, int]]:
    """Return a list of recommended jobs sorted by match score, with low matches last."""
    jobs = graph.get_all_vertices("job")
    scores = []

    for job in jobs:
        total_weight = sum(graph.get_weight(skill, job) for skill in skills if graph.has_vertex_helper(skill))
        if total_weight > 0:
            scores.append((job, total_weight))

    # Sort high scores first, but keep low matches at the bottom
    scores.sort(key=lambda x: ("[Low Match]" in x[0], -x[1], x[0]))

    # Fill remaining slots with low-match jobs if not enough
    if len(scores) < limit:
        added = set(j for j, _ in scores)
        for job in jobs:
            if job not in added:
                scores.append((job, 1))  # Default low score
            if len(scores) == limit:
                break

    return scores[:limit]


def prompt_skills() -> list[str]:
    """Prompt the user to input up to 5 skills and return them as a list of strings."""
    print("Enter up to 5 skills you have:")
    skills = []
    while len(skills) < 5:
        skill = input(f"Skill {len(skills) + 1}: ").strip()
        if skill:
            skills.append(skill)
        else:
            break
    return skills


def fetch_api_key() -> str:
    """Retrieve the Findwork API key from environment variables or .env file. Exit if missing."""
    api_key = os.getenv("FINDWORK_API_KEY")
    if not api_key:
        load_dotenv()
        api_key = os.getenv("FINDWORK_API_KEY")
    if not api_key:
        print("API key not found. Please create a .env file with FINDWORK_API_KEY=<your_key>")
        exit(1)
    return api_key


def run_job_search(user_skills: list[str], api_key: str) -> list[tuple[str, int]]:
    """Fetch jobs, build the graph, and recommend top matching jobs."""
    print("\nFetching jobs based on your skills...")
    jobs = fetch_jobs(" ".join(user_skills), api_key)
    graph = build_graph(user_skills, jobs)
    return recommend_jobs(graph, user_skills)


def display_top_jobs(top_jobs: list[tuple[str, int]]) -> None:
    """Print the list of top recommended jobs and their match levels."""
    print("\nTop Recommended Jobs:")
    if not top_jobs:
        print("Sorry, no jobs found at this time. Try again with different or more general skills.")
    else:
        for i, (job, score) in enumerate(top_jobs, 1):
            if "[Low Match]" in job:
                label = "Low Match"
            elif score >= 6:
                label = "High Match"
            elif score >= 3:
                label = "Medium Match"
            else:
                label = "Low Match"
            print(f"{i}. {job} ({label})")


def main() -> None:
    """Run the JobRec system in a loop to allow repeated use."""
    print("Welcome to JobRec! Your personal job recommendation assistant.\n")
    while True:
        user_skills = prompt_skills()
        api_key = fetch_api_key()
        top_jobs = run_job_search(user_skills, api_key)
        display_top_jobs(top_jobs)

        cont = input("\nWould you like to search again? (yes/no): ").strip().lower()
        if cont not in {'yes', 'y'}:
            print("Thanks for using JobRec. Goodbye!")
            break


if __name__ == '__main__':
    main()
    python_ta.check_all(config={
        'extra-imports': ['requests', 'dotenv', 'os', 'json', 'tkinter', 'threading', 'time'],
        'allowed-io': ['print', 'input'],
        'max-line-length': 120
    })
