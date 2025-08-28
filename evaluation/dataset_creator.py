#!/usr/bin/env python3
"""
PR Review Dataset Creation Tools
Generates synthetic and real datasets for evaluating PR review tools
"""

import json
import subprocess
import requests
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PRSample:
    """Structure for a PR review sample"""
    input: str  # Git diff content
    target: Dict[str, Any]  # Expected issues and suggestions
    metadata: Dict[str, Any]  # Additional context

class SyntheticDatasetGenerator:
    """Generate synthetic PR samples with known issues"""
    
    def __init__(self):
        self.samples = []
    
    def create_bug_samples(self) -> List[PRSample]:
        """Create samples with common bugs"""
        bug_samples = [
            # Null pointer dereference
            {
                "diff": '''diff --git a/user_service.py b/user_service.py
index 1234567..abcdefg 100644
--- a/user_service.py
+++ b/user_service.py
@@ -10,7 +10,8 @@ def get_user_profile(user_id):
     user = User.objects.get(id=user_id)
-    return {"name": user.name, "email": user.email}
+    # New feature: include profile picture
+    return {"name": user.name, "email": user.email, "avatar": user.profile.avatar_url}''',
                "issues": [
                    {
                        "type": "bug", 
                        "line": 13,
                        "description": "Potential AttributeError if user.profile is None",
                        "severity": "high",
                        "suggestion": "Add null check: user.profile.avatar_url if user.profile else None"
                    }
                ]
            },
            
            # SQL Injection
            {
                "diff": '''diff --git a/search.py b/search.py
index 1234567..abcdefg 100644
--- a/search.py
+++ b/search.py
@@ -15,7 +15,8 @@ def search_users(query):
-    users = User.objects.filter(name__icontains=query)
+    # Switch to raw SQL for better performance
+    users = User.objects.raw(f"SELECT * FROM users WHERE name LIKE '%{query}%'")''',
                "issues": [
                    {
                        "type": "security",
                        "line": 18, 
                        "description": "SQL injection vulnerability in raw query",
                        "severity": "critical",
                        "suggestion": "Use parameterized queries or stick with ORM filtering"
                    }
                ]
            },
            
            # Performance issue
            {
                "diff": '''diff --git a/blog.py b/blog.py
index 1234567..abcdefg 100644
--- a/blog.py
+++ b/blog.py
@@ -20,6 +20,9 @@ def get_blog_posts():
     posts = BlogPost.objects.all()
     result = []
     for post in posts:
+        # Add author info to each post
+        author = User.objects.get(id=post.author_id)
+        post.author_name = author.name
         result.append(post)''',
                "issues": [
                    {
                        "type": "performance",
                        "line": 24,
                        "description": "N+1 query problem - fetching author for each post separately", 
                        "severity": "medium",
                        "suggestion": "Use select_related: BlogPost.objects.select_related('author').all()"
                    }
                ]
            }
        ]
        
        return [self._create_sample(sample) for sample in bug_samples]
    
    def create_clean_samples(self) -> List[PRSample]:
        """Create samples of well-written code that should get positive feedback"""
        clean_samples = [
            {
                "diff": '''diff --git a/validator.py b/validator.py
index 1234567..abcdefg 100644
--- a/validator.py
+++ b/validator.py
@@ -10,6 +10,15 @@ from typing import Optional
 
 class EmailValidator:
     """Validates email addresses with comprehensive checks"""
+    
+    def __init__(self, allow_smtputf8: bool = True):
+        self.allow_smtputf8 = allow_smtputf8
+    
+    def validate(self, email: str) -> bool:
+        """
+        Validate email address format
+        
+        Args:
+            email: Email address to validate
+            
+        Returns:
+            bool: True if email is valid, False otherwise
+        """
+        if not email or '@' not in email:
+            return False
+            
+        try:
+            local, domain = email.rsplit('@', 1)
+            return self._validate_local(local) and self._validate_domain(domain)
+        except ValueError:
+            return False''',
                "issues": [],  # No issues - this is good code
                "feedback": [
                    "Good: Comprehensive docstrings with Args/Returns",
                    "Good: Proper error handling with try/catch", 
                    "Good: Type hints used appropriately",
                    "Good: Clear method naming and structure"
                ]
            }
        ]
        
        return [self._create_sample(sample, is_clean=True) for sample in clean_samples]
    
    def _create_sample(self, data: Dict, is_clean: bool = False) -> PRSample:
        """Convert raw data into PRSample format"""
        return PRSample(
            input=data["diff"],
            target={
                "expected_issues": data.get("issues", []),
                "expected_feedback": data.get("feedback", []),
                "is_clean_code": is_clean
            },
            metadata={
                "category": "synthetic",
                "complexity": "medium",
                "language": "python"
            }
        )

class RealDatasetCollector:
    """Collect real PR data from GitHub repositories"""
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}
    
    def collect_from_repo(self, repo: str, pr_numbers: List[int] = None) -> List[PRSample]:
        """Collect PR data from a specific repository"""
        samples = []
        
        if pr_numbers:
            # Collect specific PRs
            for pr_num in pr_numbers:
                sample = self._get_pr_sample(repo, pr_num)
                if sample:
                    samples.append(sample)
        else:
            # Collect recent merged PRs
            samples = self._get_recent_prs(repo, limit=20)
        
        return samples
    
    def _get_pr_sample(self, repo: str, pr_number: int) -> PRSample:
        """Get a single PR and convert to sample format"""
        try:
            # Get PR info
            pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
            pr_response = requests.get(pr_url, headers=self.headers)
            pr_data = pr_response.json()
            
            # Get PR diff
            diff_response = requests.get(pr_data["diff_url"], headers=self.headers)
            diff_content = diff_response.text
            
            # Get review comments for ground truth
            reviews_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
            reviews_response = requests.get(reviews_url, headers=self.headers)
            reviews = reviews_response.json()
            
            # Extract issues from reviews
            extracted_issues = self._extract_issues_from_reviews(reviews)
            
            return PRSample(
                input=diff_content,
                target={
                    "expected_issues": extracted_issues,
                    "pr_status": pr_data["state"],
                    "merge_status": pr_data["merged"]
                },
                metadata={
                    "category": "real-world",
                    "repo": repo,
                    "pr_number": pr_number,
                    "language": self._detect_language(diff_content),
                    "lines_changed": pr_data["additions"] + pr_data["deletions"]
                }
            )
            
        except Exception as e:
            print(f"Error collecting PR {pr_number}: {e}")
            return None
    
    def _extract_issues_from_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """Extract issues from GitHub review comments"""
        issues = []
        
        for review in reviews:
            if review["state"] == "CHANGES_REQUESTED":
                # Parse review body for issues
                body = review.get("body", "")
                if any(keyword in body.lower() for keyword in ["bug", "issue", "problem", "error"]):
                    issues.append({
                        "type": "review_feedback",
                        "description": body[:200] + "..." if len(body) > 200 else body,
                        "severity": "medium"
                    })
        
        return issues
    
    def _detect_language(self, diff: str) -> str:
        """Detect primary language from diff"""
        extensions = {".py": "python", ".js": "javascript", ".java": "java", 
                     ".cpp": "cpp", ".go": "go", ".rs": "rust"}
        
        for ext, lang in extensions.items():
            if ext in diff:
                return lang
        return "unknown"

class DatasetManager:
    """Main class to orchestrate dataset creation"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            # Always create datasets in the evaluation directory
            script_dir = Path(__file__).parent
            output_dir = script_dir / "datasets"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_full_dataset(self) -> Dict[str, List[PRSample]]:
        """Generate complete dataset for evaluation"""
        print("🔄 Generating synthetic samples...")
        synthetic_gen = SyntheticDatasetGenerator()
        
        datasets = {
            "bug_detection": synthetic_gen.create_bug_samples(),
            "clean_code": synthetic_gen.create_clean_samples(),
        }
        
        # Add real-world data if GitHub token available
        if os.getenv("GITHUB_TOKEN"):
            print("🔄 Collecting real-world samples...")
            real_collector = RealDatasetCollector()
            
            # Popular repos with good PR practices
            target_repos = [
                "fastapi/fastapi",
                "django/django", 
                "requests/requests"
            ]
            
            real_samples = []
            for repo in target_repos[:1]:  # Start with one repo
                try:
                    samples = real_collector.collect_from_repo(repo)
                    real_samples.extend(samples[:5])  # Limit to 5 per repo
                except Exception as e:
                    print(f"⚠️  Could not collect from {repo}: {e}")
            
            if real_samples:
                datasets["real_world"] = real_samples
        
        return datasets
    
    def save_datasets(self, datasets: Dict[str, List[PRSample]]):
        """Save datasets in Inspect AI format"""
        for name, samples in datasets.items():
            output_file = self.output_dir / f"{name}.jsonl"
            
            with open(output_file, 'w') as f:
                for sample in samples:
                    # Convert to Inspect AI format
                    inspect_sample = {
                        "input": sample.input,
                        "target": sample.target,
                        "metadata": sample.metadata
                    }
                    f.write(json.dumps(inspect_sample) + '\n')
            
            print(f"✅ Saved {len(samples)} samples to {output_file}")
    
    def create_evaluation_ready_datasets(self):
        """Main method to create all evaluation datasets"""
        print("🚀 Creating PR Review Evaluation Datasets")
        print("=" * 50)
        
        datasets = self.generate_full_dataset()
        self.save_datasets(datasets)
        
        # Create summary
        total_samples = sum(len(samples) for samples in datasets.values())
        print(f"\n📊 Dataset Summary:")
        print(f"Total samples: {total_samples}")
        for name, samples in datasets.items():
            print(f"  - {name}: {len(samples)} samples")
        
        print(f"\n💡 Next steps:")
        print(f"1. Review generated samples in {self.output_dir}")
        print(f"2. Add GITHUB_TOKEN env var for more real-world data")
        print(f"3. Customize synthetic samples for your specific needs")
        print(f"4. Run: inspect eval your_eval_task.py")

# Usage example
if __name__ == "__main__":
    # Set up GitHub token for real data collection (optional)
    # export GITHUB_TOKEN="your_token_here"
    
    manager = DatasetManager()
    manager.create_evaluation_ready_datasets()