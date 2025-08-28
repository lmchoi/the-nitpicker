## Evaluation Datasets

This tool includes a comprehensive evaluation framework using [Inspect AI](https://inspect.ai-safety-institute.org.uk/) to test and improve PR review quality across different models and scenarios.

### Quick Start

Generate evaluation datasets:
```bash
# Install evaluation dependencies
uv sync --dev

# Generate synthetic test datasets
python dataset_creator.py

# For real-world data collection (optional)
export GITHUB_TOKEN="your_github_token_here"
python dataset_creator.py
```

### Dataset Types

The dataset creator generates three types of evaluation data:

#### 1. **Bug Detection Dataset** (`datasets/bug_detection.jsonl`)
Tests the tool's ability to catch common code issues:
- **Security vulnerabilities**: SQL injection, XSS, hardcoded secrets
- **Logic errors**: Null pointer dereference, off-by-one errors
- **Performance issues**: N+1 queries, inefficient algorithms
- **Code quality**: Missing error handling, inconsistent naming

#### 2. **Clean Code Dataset** (`datasets/clean_code.jsonl`) 
Tests for false positives on well-written code:
- Properly documented functions
- Good error handling
- Appropriate type hints
- Clear naming conventions

#### 3. **Real-World Dataset** (`datasets/real_world.jsonl`)
Collected from popular open-source repositories:
- Actual PR diffs with review history
- Multiple programming languages
- Varying complexity levels
- Real reviewer feedback as ground truth

### Running Evaluations

Once datasets are created, evaluate your PR review tool:

```bash
# Run basic evaluation
inspect eval pr_review_eval.py

# Compare different models
inspect eval pr_review_eval.py --model gpt-4,claude-3-sonnet,gemini-pro

# Generate detailed reports
inspect eval pr_review_eval.py --log-dir ./eval_results
```

### Evaluation Metrics

The framework measures:
- **Precision/Recall**: How accurately issues are detected
- **False Positive Rate**: Clean code incorrectly flagged
- **Comment Quality**: Actionability, accuracy, tone, specificity
- **Coverage**: Issues caught across different categories
- **Cost Efficiency**: API usage per review

### Customizing Datasets

Add your own test cases by modifying `dataset_creator.py`:

```python
# Add custom bug patterns
custom_bugs = [
    {
        "diff": "your specific diff pattern...",
        "issues": [{
            "type": "custom_issue",
            "description": "Your issue description",
            "severity": "high"
        }]
    }
]
```

### GitHub Token Setup

For real-world data collection, create a GitHub personal access token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Create token with `public_repo` scope
3. Export as environment variable:
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

This enables collection of actual PR data from popular repositories for more realistic testing scenarios.