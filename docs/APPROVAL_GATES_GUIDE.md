# Agent Approval Gates - User Guide

## Overview

Agent Approval Gates enable **Human-in-the-Loop (HITL)** control over the EDA pipeline by pausing between each agent execution for human review and decision-making.

## What's New

### ✅ Three New Workflow Options

1. **🎯 Quick Analysis with Approval Gates**
   - Runs all 6 agents: Profile → Quality → Visualization → Feature → Stat → Transform
   - Pauses after each agent for your review
   - Best for: Complete analysis with full control

2. **🔬 Deep Dive with Approval Gates**
   - Runs 5 agents: Profile → Quality → Visualization → Feature → Stat
   - Pauses after each agent for your review
   - Best for: Thorough exploratory analysis

3. **🤖 ML Prep with Approval Gates**
   - Runs 4 agents: Profile → Quality → Feature → Transform
   - Pauses after each agent for your review
   - Best for: Machine learning preparation workflows

## How It Works

### Step 1: Start a Workflow with Approval Gates

1. Upload your dataset
2. In the sidebar, select one of the approval gate workflows:
   - "🎯 Quick Analysis with Approval Gates"
   - "🔬 Deep Dive with Approval Gates"
   - "🤖 ML Prep with Approval Gates"
3. Click the "🚀 Run with Approval Gates" button

### Step 2: Review Each Agent's Results

After each agent completes, you'll see an **Approval Gate** with:

#### Summary Metrics
- **Confidence Score**: AI's confidence in its analysis (0-100%)
- **Issues Found**: Number of data quality issues or concerns
- **Recommendations**: Number of actionable recommendations
- **Complexity**: Estimated complexity (Low 🟢 / Medium 🟡 / High 🔴)

#### Key Findings
- **🧠 Reasoning**: Why the agent analyzed the data this way
- **💡 Impact**: What impact these findings have on your analysis
- **✅ Recommendations**: Specific actionable steps

#### Detailed Results (Expandable)
- Agent-specific detailed results
- Raw data, statistics, and metrics
- Can be expanded for deeper investigation

**Special for VisualizationAgent**: 
- **📊 Thumbnail Gallery**: Preview of first 5 plots in 3-column grid
- **🔍 Expand Button**: Click to view any plot in full size
- **Quick Visual Confirmation**: Verify plots were generated correctly
- **Full Gallery**: After approval, all plots available in Visualizations tab

### Step 3: Make a Decision

You have **4 decision options**:

#### ✅ Approve & Continue to Next Agent
- Results look good
- Proceed to the next agent
- Previous agent's results will be used by subsequent agents

**When to use**: Analysis is accurate and meets expectations

#### 🔄 Retry This Agent
- Re-run this agent (useful if you changed settings or data)
- Agent will execute again with current configuration
- Previous results are discarded

**When to use**: 
- Results seem incorrect or incomplete
- You've adjusted threshold settings and want to see new results
- Agent failed due to temporary issue

#### ⏩ Skip This Agent
- Keep current results but move to next agent
- Skipped agent's results won't be used by later agents
- Workflow continues

**When to use**:
- Agent results aren't critical for your analysis
- You want to speed up the workflow
- Results are good enough to continue

#### ⏹️ Stop Workflow
- Stop the entire workflow
- All completed agents' results are saved
- Can review results so far

**When to use**:
- Found what you needed already
- Discovered critical data quality issues
- Need to fix data before continuing

## Example Workflow

### Scenario: Analyzing Customer Purchase Data

**Agent 1: ProfileAgent**
```
✅ Completed in 3.2s
📊 Results:
- 50,000 rows, 15 columns
- 10 numeric, 5 categorical columns
- Issues: 2 columns with >20% missing data

🚦 Your Decision: ✅ Approve & Continue
Reasoning: Looks good, want to see quality analysis
```

**Agent 2: QualityAgent**
```
✅ Completed in 4.1s
📊 Results:
- 5% duplicate rows
- 3 columns with outliers
- Age column has impossible values (150 years old)

🚦 Your Decision: ⏹️ Stop
Reasoning: Need to fix age data before continuing
Action: Clean data, then restart workflow
```

## Decision History

After completing or stopping a workflow, you can view your **Decision History**:

```
📋 Decision History
1. profile: ✅ approved
2. quality: ✅ approved
3. visualization: 🔄 retry (agent re-ran with new settings)
4. feature: ✅ approved
5. stat: ⏩ skip (not needed for this analysis)
6. transform: ✅ approved
```

This helps you:
- Track what decisions you made
- Understand why certain agents were skipped
- Document your analysis workflow

## Best Practices

### ✅ DO:
- **Review confidence scores**: Low confidence (<60%) means agent is uncertain
- **Check issue counts**: High issue counts (>10) need careful review
- **Read recommendations**: Agent suggestions are often actionable
- **Use retry for settings changes**: Changed a threshold? Retry the agent
- **Use skip strategically**: Not every agent is needed for every analysis

### ❌ DON'T:
- **Auto-approve without reading**: Defeats the purpose of human-in-the-loop
- **Skip critical agents**: Profile and Quality are usually essential
- **Stop too early**: Unless you found critical issues, continue to see full picture
- **Ignore low confidence**: Investigate why the agent is uncertain

## Comparison: With vs. Without Approval Gates

| Feature | Without Gates | With Approval Gates |
|---------|---------------|---------------------|
| **Control** | Run all agents automatically | Pause after each agent |
| **Review** | Only at the end | After each agent |
| **Iteration** | Re-run entire workflow | Retry individual agents |
| **Decision tracking** | None | Full decision history |
| **Time** | Faster (no pauses) | Slower (manual review) |
| **Trust** | Lower (black box) | Higher (transparent) |
| **Best for** | Quick exploration | Critical analysis |

## When to Use Approval Gates

### ✅ Use Approval Gates When:
- Analyzing critical or sensitive data (medical, financial)
- You need to explain your analysis process to stakeholders
- Data quality is unknown or suspect
- You want to learn what each agent does
- Compliance or audit requirements exist
- You're training the team on EDA pipeline

### ⚠️ Skip Approval Gates When:
- Exploring familiar, clean datasets
- Running quick tests or demos
- You trust the automated pipeline
- Time is critical
- You're doing batch processing of many datasets

## Visualization Thumbnails in Approval Gate

### What You'll See

When reviewing VisualizationAgent results, the approval gate shows a **thumbnail gallery**:

```
📊 Quick Preview (Thumbnail Gallery)
Click on any thumbnail to view full-size plot

[Thumbnail 1]    [Thumbnail 2]    [Thumbnail 3]
Distribution-Age  Box Plot-Salary  Correlation
[🔍 View Full]   [🔍 View Full]   [🔍 View Full]

[Thumbnail 4]    [Thumbnail 5]
Categorical-Dept  Distribution-Score
[🔍 View Full]   [🔍 View Full]

💡 3 more plots available in the Visualizations tab after approval
```

### Why Thumbnails, Not Full Images?

**Design Rationale**:
1. **⚡ Speed**: Approval gates are for quick decisions (30-60 sec), not deep analysis
2. **📏 Compact**: 8+ full-size plots would make the gate very long and hard to scroll
3. **🎯 Focus**: Thumbnails confirm plots were generated; details come later
4. **🔄 Workflow**: Summary during approval → Full exploration in results tab

### How to Use

**At Approval Gate**:
- ✅ **Quick visual check**: Verify plots look reasonable
- ✅ **Spot errors**: Catch obviously broken plots (blank, error messages)
- ✅ **Click to expand**: Any thumbnail can be viewed full-size if needed
- ✅ **Make decision**: Approve if plots look good, retry if something seems wrong

**After Approval (Detailed Analysis)**:
- Navigate to **"🎨 Visualizations" tab**
- All plots displayed in full size
- Interactive features available
- Export options enabled
- Scroll through complete gallery

### Best Practice

**During Approval**: 
- Quick scan of thumbnails (5-10 seconds)
- Look for obvious issues (blank plots, errors, wrong scale)
- Expand 1-2 key plots if you want to verify quality
- Approve to continue

**After Workflow**: 
- Deep dive in Visualizations tab
- Analyze each plot in detail
- Compare distributions, correlations
- Export plots for reports

## Troubleshooting

### Agent Fails During Execution
**Symptom**: Agent shows ❌ Failed status

**Solution**:
1. Check error message in UI
2. Click 🔄 Retry This Agent
3. If issue persists, check data format and size
4. Use ⏹️ Stop to investigate data issues

### Workflow Stuck on Approval Gate
**Symptom**: Can't click decision buttons

**Solution**:
1. Refresh the browser page (F5)
2. State should persist - you'll see same approval gate
3. If still stuck, click ⏹️ Stop and restart workflow

### Want to Change Settings Mid-Workflow
**Action**:
1. Note current agent
2. Click ⏹️ Stop
3. Adjust settings in sidebar
4. Restart workflow (it will be fast until the agent you stopped at)

## Technical Details

### State Management
- All decisions stored in `st.session_state.user_decisions`
- Agent results cached in `st.session_state.analysis_results`
- Workflow position tracked by `current_agent_index`

### Decision Storage Format
```python
{
    "step_id": "quality",
    "decision": "approved",
    "timestamp": "2026-07-21T10:30:45",
    "feedback": None
}
```

### Integration with Existing Features
- ✅ Works with all existing visualizations
- ✅ Compatible with export functionality
- ✅ Transformation preview/apply still works
- ✅ Progress tracking shows agent status

## Future Enhancements

Coming soon:
- 📝 **Add feedback notes** to decisions
- 🎚️ **Adjust agent parameters** at approval gate
- 📊 **View partial results** before decision
- 🔔 **Email notifications** when agent completes
- 💾 **Save decision templates** for recurring workflows

## Feedback

Found an issue or have a suggestion? Please let us know!

---

**Version**: 1.0  
**Last Updated**: 2026-07-21  
**Feature Status**: ✅ Implemented
