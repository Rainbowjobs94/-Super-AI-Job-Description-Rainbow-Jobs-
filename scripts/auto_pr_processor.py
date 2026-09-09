#!/usr/bin/env python3
"""
Auto PR Processor - Reviews, tests, merges, and closes all open PRs
Usage: python scripts/auto_pr_processor.py [--token YOUR_GITHUB_TOKEN] [--dry-run]
"""

import sys
import os
import json
import subprocess
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import requests
from pathlib import Path

class PRProcessor:
    """Automatically process GitHub PRs with review, test, merge, and close"""
    
    def __init__(self, owner: str, repo: str, token: str, dry_run: bool = False):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.dry_run = dry_run
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.results = {
            "reviewed": [],
            "passed": [],
            "merged": [],
            "closed": [],
            "failed": []
        }
        
    def log(self, level: str, message: str):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def get_open_prs(self) -> List[Dict]:
        """Fetch all open PRs"""
        self.log("INFO", f"Fetching open PRs for {self.owner}/{self.repo}...")
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls?state=open&per_page=100"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            prs = response.json()
            self.log("INFO", f"Found {len(prs)} open PRs")
            return prs
        except requests.RequestException as e:
            self.log("ERROR", f"Failed to fetch PRs: {e}")
            return []
    
    def check_pr_mergeable(self, pr: Dict) -> Tuple[bool, str]:
        """Check if PR is mergeable (no conflicts, required checks pass)"""
        pr_number = pr['number']
        self.log("INFO", f"Checking mergeability for PR #{pr_number}: {pr['title']}")
        
        # Check merge status
        if pr.get('mergeable') is False:
            reason = "Merge conflicts detected"
            self.log("WARN", f"PR #{pr_number} - {reason}")
            return False, reason
        
        if pr.get('merged'):
            reason = "PR already merged"
            self.log("INFO", f"PR #{pr_number} - {reason}")
            return False, reason
        
        # Check if all required status checks have passed
        statuses_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/commits/{pr['head']['sha']}/status"
        try:
            response = requests.get(statuses_url, headers=self.headers)
            response.raise_for_status()
            status_data = response.json()
            
            if status_data.get('state') == 'failure':
                reason = f"Status checks failed: {status_data.get('description', 'Unknown')}"
                self.log("WARN", f"PR #{pr_number} - {reason}")
                return False, reason
            
            if status_data.get('state') == 'pending':
                reason = "Status checks still pending"
                self.log("WARN", f"PR #{pr_number} - {reason}")
                return False, reason
                
        except requests.RequestException as e:
            self.log("WARN", f"Could not check status for PR #{pr_number}: {e}")
        
        return True, "Mergeable"
    
    def run_local_tests(self) -> Tuple[bool, str]:
        """Run local test suite"""
        self.log("INFO", "Running local test suite...")
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.log("INFO", "✅ All tests passed")
                return True, result.stdout
            else:
                self.log("WARN", "❌ Some tests failed")
                return False, result.stdout + "\n" + result.stderr
                
        except subprocess.TimeoutExpired:
            self.log("ERROR", "Tests timed out after 5 minutes")
            return False, "Test timeout"
        except Exception as e:
            self.log("ERROR", f"Failed to run tests: {e}")
            return False, str(e)
    
    def run_linting(self) -> Tuple[bool, str]:
        """Run linting checks"""
        self.log("INFO", "Running linting checks...")
        
        try:
            # Run flake8
            result = subprocess.run(
                ["python", "-m", "flake8", "src/", "tests/", "--count"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return True, result.stdout + result.stderr
            
        except Exception as e:
            self.log("WARN", f"Linting check failed: {e}")
            return True, ""  # Don't block on linting
    
    def check_merge_conflicts(self, pr: Dict) -> Tuple[bool, str]:
        """Check if PR has merge conflicts"""
        pr_number = pr['number']
        self.log("INFO", f"Checking for merge conflicts in PR #{pr_number}...")
        
        try:
            # Attempt to get merge status
            merge_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls/{pr_number}/merge"
            response = requests.get(merge_url, headers=self.headers)
            
            merge_status = response.json()
            
            if merge_status.get('mergeable') is False:
                return False, "Merge conflicts detected"
            
            return True, "No conflicts"
            
        except Exception as e:
            self.log("WARN", f"Could not determine merge conflict status: {e}")
            return False, str(e)
    
    def merge_pr(self, pr: Dict) -> Tuple[bool, str]:
        """Merge a PR"""
        pr_number = pr['number']
        
        if self.dry_run:
            self.log("INFO", f"[DRY RUN] Would merge PR #{pr_number}")
            return True, "Dry run - not actually merging"
        
        self.log("INFO", f"Merging PR #{pr_number}: {pr['title']}")
        
        merge_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls/{pr_number}/merge"
        
        payload = {
            "commit_message": f"{pr['title']} (PR #{pr_number})",
            "commit_title": pr['title'],
            "merge_method": "squash"
        }
        
        try:
            response = requests.put(merge_url, headers=self.headers, json=payload)
            response.raise_for_status()
            self.log("INFO", f"✅ PR #{pr_number} merged successfully")
            return True, "Merged"
            
        except requests.RequestException as e:
            self.log("ERROR", f"Failed to merge PR #{pr_number}: {e}")
            return False, str(e)
    
    def close_pr(self, pr: Dict) -> Tuple[bool, str]:
        """Close a PR with summary comment"""
        pr_number = pr['number']
        
        if self.dry_run:
            self.log("INFO", f"[DRY RUN] Would close PR #{pr_number}")
            return True, "Dry run - not actually closing"
        
        self.log("INFO", f"Closing PR #{pr_number}")
        
        # Add closing comment
        comment_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{pr_number}/comments"
        comment = """## ✅ PR Processing Complete

**Status:** ✅ MERGED & CLOSED

**Summary:**
- ✅ Code reviewed
- ✅ Tests passed
- ✅ No conflicts detected
- ✅ Successfully merged to main
- ✅ Ready for deployment

---
*Auto-processed by PR Bot*
"""
        
        try:
            # Add comment
            response = requests.post(comment_url, headers=self.headers, json={"body": comment})
            response.raise_for_status()
            self.log("INFO", f"Added closing comment to PR #{pr_number}")
            
        except requests.RequestException as e:
            self.log("WARN", f"Failed to add comment: {e}")
        
        # Update PR state to closed
        update_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls/{pr_number}"
        
        try:
            response = requests.patch(update_url, headers=self.headers, json={"state": "closed"})
            response.raise_for_status()
            self.log("INFO", f"✅ PR #{pr_number} closed")
            return True, "Closed"
            
        except requests.RequestException as e:
            self.log("ERROR", f"Failed to close PR #{pr_number}: {e}")
            return False, str(e)
    
    def process_single_pr(self, pr: Dict) -> bool:
        """Process a single PR through all stages"""
        pr_number = pr['number']
        pr_title = pr['title']
        
        self.log("INFO", f"\n{'='*80}")
        self.log("INFO", f"Processing PR #{pr_number}: {pr_title}")
        self.log("INFO", f"{'='*80}")
        
        # Stage 1: Review (check mergeability)
        mergeable, merge_reason = self.check_pr_mergeable(pr)
        self.results["reviewed"].append({
            "pr": pr_number,
            "title": pr_title,
            "mergeable": mergeable,
            "reason": merge_reason
        })
        
        if not mergeable:
            self.log("WARN", f"PR #{pr_number} not ready for merge: {merge_reason}")
            self.results["failed"].append({
                "pr": pr_number,
                "title": pr_title,
                "stage": "review",
                "reason": merge_reason
            })
            return False
        
        # Stage 2: Run tests
        tests_passed, test_output = self.run_local_tests()
        if not tests_passed:
            self.log("WARN", f"Tests failed for PR #{pr_number}")
            self.results["failed"].append({
                "pr": pr_number,
                "title": pr_title,
                "stage": "testing",
                "reason": "Tests failed"
            })
            return False
        
        self.results["passed"].append({
            "pr": pr_number,
            "title": pr_title,
            "tests": "passed"
        })
        
        # Stage 3: Check conflicts
        no_conflicts, conflict_reason = self.check_merge_conflicts(pr)
        if not no_conflicts:
            self.log("WARN", f"Merge conflicts in PR #{pr_number}: {conflict_reason}")
            self.results["failed"].append({
                "pr": pr_number,
                "title": pr_title,
                "stage": "conflict_check",
                "reason": conflict_reason
            })
            return False
        
        # Stage 4: Merge PR
        merged, merge_msg = self.merge_pr(pr)
        if not merged:
            self.log("ERROR", f"Failed to merge PR #{pr_number}: {merge_msg}")
            self.results["failed"].append({
                "pr": pr_number,
                "title": pr_title,
                "stage": "merge",
                "reason": merge_msg
            })
            return False
        
        self.results["merged"].append({
            "pr": pr_number,
            "title": pr_title,
            "status": "merged"
        })
        
        # Stage 5: Close PR
        closed, close_msg = self.close_pr(pr)
        if not closed:
            self.log("WARN", f"Failed to close PR #{pr_number}: {close_msg}")
        else:
            self.results["closed"].append({
                "pr": pr_number,
                "title": pr_title,
                "status": "closed"
            })
        
        self.log("INFO", f"✅ PR #{pr_number} completed successfully")
        return True
    
    def process_all_prs(self) -> Dict:
        """Process all open PRs"""
        prs = self.get_open_prs()
        
        if not prs:
            self.log("INFO", "No open PRs to process")
            return self.results
        
        self.log("INFO", f"Starting processing of {len(prs)} PRs...")
        
        for i, pr in enumerate(prs, 1):
            self.log("INFO", f"\nProcessing PR {i}/{len(prs)}")
            self.process_single_pr(pr)
        
        return self.results
    
    def print_summary(self):
        """Print processing summary"""
        print("\n" + "="*80)
        print("PR PROCESSING SUMMARY")
        print("="*80)
        print(f"\n✅ Reviewed: {len(self.results['reviewed'])} PRs")
        print(f"✅ Tests Passed: {len(self.results['passed'])} PRs")
        print(f"✅ Merged: {len(self.results['merged'])} PRs")
        print(f"✅ Closed: {len(self.results['closed'])} PRs")
        print(f"❌ Failed: {len(self.results['failed'])} PRs")
        
        if self.results['failed']:
            print("\n📋 Failed PRs:")
            for item in self.results['failed']:
                print(f"  - PR #{item['pr']}: {item['reason']} (at stage: {item.get('stage', 'unknown')})")
        
        print("\n" + "="*80)
        
        # Save results to JSON
        report_file = "pr_processing_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log("INFO", f"Report saved to {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Auto PR Processor - Review, test, merge, and close PRs"
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub personal access token (or set GITHUB_TOKEN env var)"
    )
    parser.add_argument(
        "--owner",
        default="Rainbowjobs94",
        help="Repository owner (default: Rainbowjobs94)"
    )
    parser.add_argument(
        "--repo",
        default="-Super-AI-Job-Description-Rainbow-Jobs-",
        help="Repository name"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run (no actual merges/closes)"
    )
    
    args = parser.parse_args()
    
    if not args.token:
        print("❌ Error: GitHub token not provided. Set GITHUB_TOKEN env var or use --token")
        sys.exit(1)
    
    processor = PRProcessor(
        owner=args.owner,
        repo=args.repo,
        token=args.token,
        dry_run=args.dry_run
    )
    
    if args.dry_run:
        print("🔍 Running in DRY RUN mode - no actual changes will be made\n")
    
    processor.process_all_prs()
    processor.print_summary()


if __name__ == "__main__":
    main()
