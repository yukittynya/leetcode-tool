#!/usr/bin/env python3

import sys
import re
import requests
from pathlib import Path
from typing import Any, Dict

class Tool:
    def __init__(self):
        self.language = ''
        self.languages = [
            'c',
            'cpp',
            'c#',
            'csharp',
            'go',
            'java',
            'javascript',
            'js',
            'kotlin',
            'php',
            'python',
            'ruby',
            'rust',
            'scala',
            'swift',
            'ts',
            'tsx',
            'typescript',
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

    def extract_problem_slug(self, url_or_slug: str) -> str:
        if url_or_slug.startswith('http'):
            match = re.search(r'/problems/([^/]+)/?', url_or_slug)

            if match:
                return match.group(1)

        return url_or_slug
    
    def get_problem_data(self, problem_slug: str) -> Dict[str, Any]:
        query = """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                content
                difficulty
                topicTags {
                    name
                }
                codeSnippets {
                    lang
                    langSlug
                    code
                }
                sampleTestCase
                exampleTestcases
            }
        }
        """
        
        variables = {"titleSlug": problem_slug}
        
        try:
            response = self.session.post(
                'https://leetcode.com/graphql',
                json={'query': query, 'variables': variables}
            )
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                raise Exception(f"GraphQL Error: {data['errors']}")

            return data['data']['question']
        except Exception as e:
            print(f"Error fetching problem data: {e}")
            sys.exit(1)
    
    def clean_html(self, html_content: str) -> str:
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        clean_text = clean_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&nbsp;', '\n')
        clean_text = clean_text.replace('&quot;', '"').replace('&#39;', "'")
        clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
        clean_text = clean_text.strip()

        return clean_text

    def create_dir(self, problem_data: Dict[str, Any]) -> str:
        ext_map = {
            'c': 'c',
            'cpp': 'cpp',
            'c#': 'cs',
            'csharp': 'cs',
            'go': 'go',
            'java': 'java',
            'javascript': 'js',
            'js': 'js',
            'kotlin': 'kt',
            'php': 'php',
            'python': 'py',
            'ruby': 'rb',
            'rust': 'rs',
            'scala': 'scala',
            'swift': 'swift',
            'ts': 'ts',
            'tsx': 'ts',
            'typescript': 'ts',

        }

        id = problem_data['questionFrontendId']
        title = problem_data['titleSlug']
        dir_name = f"{id}-{title}"

        Path(dir_name).mkdir(exist_ok=True)

        readme_content = f"""# {problem_data['title']}

**URL:** https://leetcode.com/problems/{title}/
**Difficulty:** {problem_data['difficulty']}

## Problem Description

{self.clean_html(problem_data['content'])}

## Tags
{', '.join([tag['name'] for tag in problem_data['topicTags']])}
"""
        with open(f"{dir_name}/README.md", 'w') as f:
            f.write(readme_content)

        for snippet in problem_data['codeSnippets']:
            lang = snippet['langSlug']
            code = snippet['code']

            if self.language == lang in ext_map:
                filename = f"{dir_name}/solution.{ext_map[self.language]}"
                with open(filename, 'w') as f:
                    f.write(code)
        return dir_name

    def get_language(self, language: str) -> str:
        if language.lower() in self.languages:
            return language.lower()
        else:
            return "n/a"

    def run_tests(self):
        return

def main():
    tool = Tool()

    if len(sys.argv) < 2:
        print("Usage:\n")
        print("\t\tleetcode [language] <url to problem>")
        print("\t\tleetcode test <problem directory>")
        sys.exit(1)

    if sys.argv[1] == 'test':
        if len(sys.argv) < 3:
            print("Usage:\n")
            print("\t\tleetcode test <problem directory>")
            sys.exit(1)

        tool.run_tests()

    else:
        tool.language = tool.get_language(sys.argv[1])

        if tool.language == "n/a":
            print("Not valid language, supported languages:")
            for lang in tool.languages:
                print(f"\t{lang}")

            sys.exit(1)

        problem_slug = tool.extract_problem_slug(sys.argv[2])
        print(f"Fetching {problem_slug}")
        problem_data = tool.get_problem_data(problem_slug)

        if not problem_slug:
            print(f"Failed to read {problem_slug}")
            sys.exit(1)

        print(f"Creating directory for: {problem_data['title']}")
        print(f"Problem created in {tool.create_dir(problem_data)}")

if __name__ == "__main__":
    main()
