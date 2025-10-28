# Meta Prompt Templates Library

A comprehensive collection of multi-step AI workflow templates for Excel AI Assistant.

---

## Table of Contents

1. [Data Cleaning & Validation](#data-cleaning--validation)
2. [Content Analysis](#content-analysis)
3. [Content Generation](#content-generation)
4. [Data Enrichment](#data-enrichment)
5. [Business Intelligence](#business-intelligence)
6. [Communication](#communication)
7. [Research & Analysis](#research--analysis)
8. [E-commerce](#e-commerce)
9. [HR & Recruiting](#hr--recruiting)
10. [Financial Analysis](#financial-analysis)

---

## Data Cleaning & Validation

### 1. Complete Data Cleanup Pipeline

**Use Case:** Comprehensive data quality improvement

**Execution Time:** ~2-3 seconds per row

```yaml
id: cleanup_001
name: "Complete Data Cleanup"
category: "data_cleaning"
description: "Multi-stage data cleaning workflow with validation"
difficulty: "medium"

context_columns: []  # Can use any columns for context

steps:
  - id: "step_1"
    name: "Remove extra whitespace"
    prompt: "Remove all leading, trailing, and extra whitespace from this text. Preserve intentional line breaks."
    temperature: 0.1
    max_tokens: 200

  - id: "step_2"
    name: "Fix text encoding"
    prompt: "Fix any text encoding issues including: garbled characters, HTML entities (&nbsp;, &amp;, etc.), Unicode errors, and special character corruption. Return clean text."
    temperature: 0.2
    max_tokens: 200

  - id: "step_3"
    name: "Standardize capitalization"
    prompt: "Apply proper capitalization based on content type: Title Case for names, lowercase for emails, Sentence case for descriptions. Return standardized text."
    temperature: 0.1
    max_tokens: 200

  - id: "step_4"
    name: "Validate and flag issues"
    prompt: "Check for remaining data quality issues: incomplete data, invalid characters, inconsistent formatting. Return the cleaned text, or if issues remain, prepend '[FLAG: {issue}] ' to the text."
    temperature: 0.2
    max_tokens: 250

output_columns:
  - "Cleaned_Text"
  - "Quality_Status"
```

### 2. Email Validation & Enhancement

**Use Case:** Clean, validate, and enrich email addresses

```yaml
id: cleanup_002
name: "Email Validation & Enhancement"
category: "data_cleaning"
description: "Extract, clean, validate, and categorize email addresses"

steps:
  - id: "step_1"
    name: "Extract email"
    prompt: "Extract the email address from this text, removing any surrounding characters, labels, or markup. Return only the email address."
    temperature: 0.1
    max_tokens: 50

  - id: "step_2"
    name: "Lowercase and trim"
    prompt: "Convert this email to lowercase and remove all whitespace."
    temperature: 0.0
    max_tokens: 50

  - id: "step_3"
    name: "Validate format"
    prompt: "Validate this email format. Return 'VALID' if format is correct (has @ symbol, valid domain structure, no invalid characters). Return 'INVALID: {reason}' if not valid."
    temperature: 0.1
    max_tokens: 100

  - id: "step_4"
    name: "Domain categorization"
    prompt: "Categorize the email domain as: 'Business' (company domain), 'Personal' (Gmail, Yahoo, etc.), 'Education' (.edu), 'Government' (.gov), or 'Suspicious' (disposable email, typosquatting). Return category only."
    temperature: 0.2
    max_tokens: 30

  - id: "step_5"
    name: "Risk assessment"
    prompt: "Assess email risk level: 'Low' (verified business/education), 'Medium' (personal email), or 'High' (disposable, suspicious pattern, or invalid). Return risk level only."
    temperature: 0.2
    max_tokens: 20

output_columns:
  - "Email_Clean"
  - "Email_Valid"
  - "Domain_Type"
  - "Risk_Level"
```

### 3. Phone Number Standardization

**Use Case:** Format phone numbers consistently

```yaml
id: cleanup_003
name: "Phone Number Standardization"
category: "data_cleaning"

steps:
  - id: "step_1"
    name: "Extract phone number"
    prompt: "Extract phone number from this text, removing all non-numeric characters except + symbol."
    temperature: 0.0
    max_tokens: 50

  - id: "step_2"
    name: "Detect country"
    prompt: "Based on this phone number, identify the country code. Return country code or 'Unknown'."
    temperature: 0.1
    max_tokens: 30

  - id: "step_3"
    name: "Format international"
    prompt: "Format this phone number in international format: +[country code] ([area code]) [number]. If country code unknown, assume +1 (US/Canada)."
    temperature: 0.1
    max_tokens: 50

  - id: "step_4"
    name: "Validate"
    prompt: "Check if this phone number has the correct number of digits for its country. Return 'VALID' or 'INVALID: {reason}'."
    temperature: 0.1
    max_tokens: 50

output_columns:
  - "Phone_Standardized"
  - "Country_Code"
  - "Phone_Valid"
```

### 4. Address Parsing & Validation

**Use Case:** Structure and validate addresses

```yaml
id: cleanup_004
name: "Address Parser & Validator"
category: "data_cleaning"

steps:
  - id: "step_1"
    name: "Parse street address"
    prompt: "Extract the street address (number and street name) from this address. Return only the street portion."
    temperature: 0.1
    max_tokens: 100
    output_column: "Street"

  - id: "step_2"
    name: "Parse city"
    prompt: "Extract the city name from this address."
    temperature: 0.1
    max_tokens: 50
    output_column: "City"

  - id: "step_3"
    name: "Parse state/province"
    prompt: "Extract the state or province from this address. Use 2-letter abbreviation if applicable."
    temperature: 0.1
    max_tokens: 30
    output_column: "State"

  - id: "step_4"
    name: "Parse postal code"
    prompt: "Extract the postal/ZIP code from this address."
    temperature: 0.0
    max_tokens: 30
    output_column: "Postal_Code"

  - id: "step_5"
    name: "Parse country"
    prompt: "Extract or infer the country from this address. Return ISO 2-letter country code (e.g., US, CA, GB)."
    temperature: 0.1
    max_tokens: 20
    output_column: "Country"

  - id: "step_6"
    name: "Standardize format"
    prompt: "Rewrite this address in standard format: [Street], [City], [State] [Postal Code], [Country]"
    temperature: 0.1
    max_tokens: 150
    output_column: "Address_Standardized"
```

---

## Content Analysis

### 5. Sentiment Analysis Suite

**Use Case:** Comprehensive sentiment and emotion analysis

```yaml
id: analysis_001
name: "Comprehensive Sentiment Analysis"
category: "content_analysis"
description: "Multi-dimensional sentiment and emotion detection"

steps:
  - id: "step_1"
    name: "Sentiment classification"
    prompt: "Classify the overall sentiment of this text. Return exactly one of: Positive, Negative, Neutral, or Mixed."
    temperature: 0.2
    max_tokens: 20
    output_column: "Sentiment"

  - id: "step_2"
    name: "Sentiment score"
    prompt: "Rate the sentiment intensity on a scale from -5 (very negative) to +5 (very positive). Consider strength of language and emotional indicators. Return only the number."
    temperature: 0.3
    max_tokens: 10
    output_column: "Sentiment_Score"

  - id: "step_3"
    name: "Emotion detection"
    prompt: "Identify the primary emotion expressed in this text. Choose from: joy, sadness, anger, fear, surprise, disgust, trust, anticipation, or neutral. Return only the emotion."
    temperature: 0.2
    max_tokens: 30
    output_column: "Primary_Emotion"

  - id: "step_4"
    name: "Secondary emotions"
    prompt: "Identify any secondary emotions present (max 2). Format as comma-separated list, or 'None' if only one emotion."
    temperature: 0.2
    max_tokens: 50
    output_column: "Secondary_Emotions"

  - id: "step_5"
    name: "Confidence level"
    prompt: "Rate your confidence in the sentiment analysis from 1 (low confidence, ambiguous) to 5 (high confidence, clear sentiment). Return only the number."
    temperature: 0.2
    max_tokens: 10
    output_column: "Analysis_Confidence"
```

### 6. Customer Feedback Analyzer

**Use Case:** Structured analysis of customer feedback

```yaml
id: analysis_002
name: "Customer Feedback Analysis"
category: "content_analysis"
context_columns: ["Customer_Name", "Product", "Date", "Order_ID"]

steps:
  - id: "step_1"
    name: "Categorize feedback"
    prompt: "Categorize this customer feedback into exactly one category: Feature Request, Bug Report, Complaint, Praise, Question, Suggestion, or Other."
    temperature: 0.2
    max_tokens: 30
    output_column: "Feedback_Type"

  - id: "step_2"
    name: "Priority assessment"
    prompt: "Assess the priority of this feedback based on urgency, customer impact, and severity. Return: Critical, High, Medium, or Low."
    temperature: 0.3
    max_tokens: 20
    output_column: "Priority"

  - id: "step_3"
    name: "Product areas"
    prompt: "Identify which product features or areas are mentioned in this feedback. Return as comma-separated list."
    temperature: 0.2
    max_tokens: 100
    output_column: "Features_Mentioned"

  - id: "step_4"
    name: "Customer sentiment score"
    prompt: "Rate customer satisfaction from 1 (very dissatisfied) to 5 (very satisfied). Consider tone, language, and content. Return only the number."
    temperature: 0.2
    max_tokens: 10
    output_column: "CSAT_Score"

  - id: "step_5"
    name: "Churn risk"
    prompt: "Assess churn risk based on this feedback. Return: High (likely to churn), Medium (at risk), or Low (satisfied/retained)."
    temperature: 0.3
    max_tokens: 20
    output_column: "Churn_Risk"

  - id: "step_6"
    name: "Executive summary"
    prompt: "Create a concise one-sentence executive summary of this feedback that captures the key issue or praise."
    temperature: 0.3
    max_tokens: 100
    output_column: "Summary"

  - id: "step_7"
    name: "Recommended actions"
    prompt: "Recommend specific next steps for the support/product team to address this feedback. Be actionable and specific."
    temperature: 0.4
    max_tokens: 150
    output_column: "Next_Steps"
```

### 7. Content Quality Scorer

**Use Case:** Evaluate content quality objectively

```yaml
id: analysis_003
name: "Content Quality Assessment"
category: "content_analysis"

steps:
  - id: "step_1"
    name: "Readability score"
    prompt: "Rate the readability of this text from 1-10 (1=very complex/hard to read, 10=very clear/easy to read). Consider sentence structure, vocabulary, and clarity."
    temperature: 0.2
    max_tokens: 10
    output_column: "Readability"

  - id: "step_2"
    name: "Grammar quality"
    prompt: "Rate grammar and spelling quality from 1-10 (1=many errors, 10=flawless). Note major issues if any."
    temperature: 0.2
    max_tokens: 50
    output_column: "Grammar_Score"

  - id: "step_3"
    name: "Completeness"
    prompt: "Rate content completeness from 1-10 (1=very incomplete/vague, 10=comprehensive/detailed). Does it fully address its topic?"
    temperature: 0.3
    max_tokens: 10
    output_column: "Completeness"

  - id: "step_4"
    name: "Professionalism"
    prompt: "Rate professionalism from 1-10 (1=very casual/inappropriate, 10=highly professional). Consider tone, language, and formality."
    temperature: 0.2
    max_tokens: 10
    output_column: "Professionalism"

  - id: "step_5"
    name: "Engagement score"
    prompt: "Rate how engaging/compelling this content is from 1-10 (1=boring/dry, 10=very engaging/interesting)."
    temperature: 0.3
    max_tokens: 10
    output_column: "Engagement"

  - id: "step_6"
    name: "Overall quality"
    prompt: "Calculate overall content quality score from 1-100 based on all factors. Return only the number."
    temperature: 0.2
    max_tokens: 10
    output_column: "Overall_Quality"

  - id: "step_7"
    name: "Improvement suggestions"
    prompt: "Provide 2-3 specific suggestions to improve this content."
    temperature: 0.4
    max_tokens: 200
    output_column: "Suggestions"
```

---

## Content Generation

### 8. Product Description Generator

**Use Case:** Generate marketing copy for products

```yaml
id: generation_001
name: "Product Description Generator"
category: "content_generation"
context_columns: ["Product_Name", "Category", "Price", "Features", "Brand"]

steps:
  - id: "step_1"
    name: "Headline"
    prompt: "Create a compelling, benefit-focused headline for this product (max 60 characters). Focus on the primary value proposition."
    temperature: 0.7
    max_tokens: 50
    output_column: "Headline"

  - id: "step_2"
    name: "Short description"
    prompt: "Write a compelling one-sentence product description (max 150 chars) that highlights the key benefit and creates urgency."
    temperature: 0.7
    max_tokens: 100
    output_column: "Short_Description"

  - id: "step_3"
    name: "Long description"
    prompt: "Write a detailed 3-paragraph product description:\n- Paragraph 1: Hook and primary benefit\n- Paragraph 2: Key features and how they help\n- Paragraph 3: Call to action\nMake it engaging and benefit-focused, not just feature-focused."
    temperature: 0.7
    max_tokens: 400
    output_column: "Long_Description"

  - id: "step_4"
    name: "Key benefits list"
    prompt: "List 5 key benefits (not features) as concise bullet points. Each should explain how the product improves the customer's life. Format with bullet points."
    temperature: 0.7
    max_tokens: 200
    output_column: "Key_Benefits"

  - id: "step_5"
    name: "SEO title"
    prompt: "Create an SEO-optimized title (max 60 chars) that includes key search terms while remaining compelling. Format: [Product Name] - [Key Benefit] - [Brand]"
    temperature: 0.6
    max_tokens: 70
    output_column: "SEO_Title"

  - id: "step_6"
    name: "Meta description"
    prompt: "Write a meta description for search engines (max 155 chars) that includes key benefits and a subtle CTA."
    temperature: 0.6
    max_tokens: 100
    output_column: "Meta_Description"

  - id: "step_7"
    name: "Target audience"
    prompt: "Describe the ideal customer for this product in one sentence. Include demographics, psychographics, and pain points."
    temperature: 0.5
    max_tokens: 100
    output_column: "Target_Audience"
```

### 9. Social Media Content Suite

**Use Case:** Generate platform-specific social content

```yaml
id: generation_002
name: "Multi-Platform Social Media Content"
category: "content_generation"
context_columns: ["Topic", "Brand_Voice", "Key_Message", "CTA"]

steps:
  - id: "step_1"
    name: "Twitter/X post"
    prompt: "Create an engaging Twitter/X post (max 280 characters) about this topic. Include 2-3 relevant hashtags. Make it shareable and engaging."
    temperature: 0.8
    max_tokens: 100
    output_column: "Twitter_Post"

  - id: "step_2"
    name: "LinkedIn post"
    prompt: "Write a professional LinkedIn post (max 1300 chars) with:\n- Hook (first line)\n- Value/insight (middle paragraphs)\n- Call-to-action (end)\nUse short paragraphs and line breaks for readability."
    temperature: 0.7
    max_tokens: 500
    output_column: "LinkedIn_Post"

  - id: "step_3"
    name: "Instagram caption"
    prompt: "Create an Instagram caption with:\n- Engaging opening line\n- Story or value (2-3 paragraphs)\n- Call-to-action\n- 15-20 relevant hashtags\n- Use emojis strategically"
    temperature: 0.8
    max_tokens: 600
    output_column: "Instagram_Caption"

  - id: "step_4"
    name: "Facebook post"
    prompt: "Write an engaging Facebook post (max 400 characters) that:\n- Starts with a hook or question\n- Provides value or tells a story\n- Ends with an engagement prompt (question, poll idea)\nUse conversational tone."
    temperature: 0.7
    max_tokens: 300
    output_column: "Facebook_Post"

  - id: "step_5"
    name: "Thread opener"
    prompt: "Create the first tweet of a Twitter/X thread that hooks readers and promises value. End with '(1/x) 🧵' to indicate thread."
    temperature: 0.8
    max_tokens: 100
    output_column: "Thread_Opener"

  - id: "step_6"
    name: "Pinterest description"
    prompt: "Write a Pinterest pin description (max 500 chars) optimized for search with relevant keywords, clear value proposition, and CTA."
    temperature: 0.7
    max_tokens: 200
    output_column: "Pinterest_Description"
```

### 10. Email Campaign Generator

**Use Case:** Create email marketing content

```yaml
id: generation_003
name: "Email Marketing Campaign"
category: "content_generation"
context_columns: ["Campaign_Goal", "Audience", "Product", "Offer"]

steps:
  - id: "step_1"
    name: "Subject line A"
    prompt: "Create a compelling email subject line (max 50 chars) that drives opens. Use curiosity, urgency, or value proposition. Be specific and avoid spam words."
    temperature: 0.8
    max_tokens: 60
    output_column: "Subject_Line_A"

  - id: "step_2"
    name: "Subject line B"
    prompt: "Create an alternative email subject line with a different angle or approach (max 50 chars). Make it significantly different from the first option."
    temperature: 0.8
    max_tokens: 60
    output_column: "Subject_Line_B"

  - id: "step_3"
    name: "Preview text"
    prompt: "Write preview/preheader text (max 90 chars) that complements the subject line and provides additional context or value."
    temperature: 0.7
    max_tokens: 100
    output_column: "Preview_Text"

  - id: "step_4"
    name: "Email body"
    prompt: "Write a complete email body with:\n- Personal greeting\n- Hook (attention-grabbing opener)\n- Problem/situation (relate to reader)\n- Solution (your offer)\n- Benefits (bullet points)\n- Social proof (brief)\n- Clear CTA\n- Sign-off\nKeep paragraphs short. Use conversational tone."
    temperature: 0.7
    max_tokens: 800
    output_column: "Email_Body"

  - id: "step_5"
    name: "CTA button text"
    prompt: "Create compelling CTA button text (2-5 words) that's action-oriented and creates urgency. Be specific about what happens next."
    temperature: 0.7
    max_tokens: 30
    output_column: "CTA_Text"

  - id: "step_6"
    name: "PS line"
    prompt: "Write a P.S. line that adds urgency, provides additional value, or reinforces the offer. P.S. lines have high readership."
    temperature: 0.7
    max_tokens: 100
    output_column: "PS_Line"
```

---

## Data Enrichment

### 11. Company Intelligence Enrichment

**Use Case:** Enrich company records with insights

```yaml
id: enrichment_001
name: "Company Intelligence Enrichment"
category: "data_enrichment"
context_columns: ["Company_Name", "Website", "Industry", "Location"]

steps:
  - id: "step_1"
    name: "Company size estimation"
    prompt: "Based on the company information provided, estimate company size. Return one of: Startup (<50 employees), Small (50-200), Medium (200-1000), Large (1000-5000), Enterprise (5000+)."
    temperature: 0.3
    max_tokens: 30
    output_column: "Estimated_Size"

  - id: "step_2"
    name: "Industry classification"
    prompt: "Classify this company's industry more specifically. Format as: [Primary Industry] > [Sub-industry]. Example: 'Technology > SaaS'"
    temperature: 0.2
    max_tokens: 50
    output_column: "Industry_Detail"

  - id: "step_3"
    name: "Technology stack"
    prompt: "Based on industry, size, and other signals, predict likely technology stack. List 5-7 technologies they probably use. Format as comma-separated list."
    temperature: 0.4
    max_tokens: 150
    output_column: "Likely_Tech_Stack"

  - id: "step_4"
    name: "Key decision makers"
    prompt: "Identify 3-4 job titles of key decision-makers for B2B purchases at this company. Consider company size and industry. Format as comma-separated list."
    temperature: 0.3
    max_tokens: 100
    output_column: "Decision_Maker_Titles"

  - id: "step_5"
    name: "Business priorities"
    prompt: "Based on industry and size, list 3-5 likely business priorities or initiatives for this type of company in 2025."
    temperature: 0.4
    max_tokens: 200
    output_column: "Likely_Priorities"

  - id: "step_6"
    name: "Pain points"
    prompt: "Identify 4-6 common pain points or challenges faced by companies of this type and size. Be specific to their industry and stage."
    temperature: 0.4
    max_tokens: 250
    output_column: "Common_Pain_Points"

  - id: "step_7"
    name: "Buying patterns"
    prompt: "Describe typical buying patterns for this company type: procurement process, decision timeline, budget cycles, key evaluation criteria."
    temperature: 0.4
    max_tokens: 200
    output_column: "Buying_Behavior"
```

### 12. Lead Scoring & Qualification

**Use Case:** Score and qualify sales leads

```yaml
id: enrichment_002
name: "Lead Scoring & Qualification"
category: "data_enrichment"
context_columns: ["Company", "Title", "Industry", "Company_Size", "Engagement"]

steps:
  - id: "step_1"
    name: "Title relevance score"
    prompt: "Rate how relevant this job title is to B2B software purchasing decisions. Score 1-10 (1=not relevant, 10=primary decision maker). Return only number."
    temperature: 0.2
    max_tokens: 10
    output_column: "Title_Score"

  - id: "step_2"
    name: "Company fit score"
    prompt: "Based on industry and company size, rate how well this fits our ideal customer profile. Score 1-10 (1=poor fit, 10=perfect fit). Return only number."
    temperature: 0.3
    max_tokens: 10
    output_column: "Company_Fit_Score"

  - id: "step_3"
    name: "Engagement score"
    prompt: "Based on engagement data, rate lead engagement level. Score 1-10 (1=cold/unengaged, 10=very engaged). Return only number."
    temperature: 0.3
    max_tokens: 10
    output_column: "Engagement_Score"

  - id: "step_4"
    name: "Budget likelihood"
    prompt: "Estimate likelihood this lead has budget for enterprise software. Return: High, Medium, or Low."
    temperature: 0.3
    max_tokens: 20
    output_column: "Budget_Likelihood"

  - id: "step_5"
    name: "Timing score"
    prompt: "Based on all signals, estimate purchase timing. Return: Immediate (0-3 months), Near-term (3-6 months), Long-term (6+ months), or Unlikely."
    temperature: 0.3
    max_tokens: 30
    output_column: "Purchase_Timing"

  - id: "step_6"
    name: "Overall lead score"
    prompt: "Calculate overall lead score from 1-100 considering all factors: title relevance, company fit, engagement, budget, and timing. Return only number."
    temperature: 0.2
    max_tokens: 10
    output_column: "Lead_Score"

  - id: "step_7"
    name: "Lead grade"
    prompt: "Assign lead grade based on overall score: A (90-100), B (70-89), C (50-69), D (30-49), F (<30). Return only the letter."
    temperature: 0.1
    max_tokens: 10
    output_column: "Lead_Grade"

  - id: "step_8"
    name: "Recommended action"
    prompt: "Recommend specific next action for sales team based on lead score and profile. Be specific and actionable."
    temperature: 0.4
    max_tokens: 150
    output_column: "Next_Action"
```

---

## Business Intelligence

### 13. Competitive Intelligence Analyzer

**Use Case:** Analyze competitor information

```yaml
id: business_001
name: "Competitive Analysis Workflow"
category: "business_intelligence"
context_columns: ["Competitor_Name", "Website", "Product", "Market_Position"]

steps:
  - id: "step_1"
    name: "Value proposition"
    prompt: "Describe this competitor's unique value proposition in one sentence. What makes them different?"
    temperature: 0.3
    max_tokens: 150
    output_column: "Value_Proposition"

  - id: "step_2"
    name: "Top strengths"
    prompt: "List their top 3-5 competitive strengths. What do they do exceptionally well? Format as bullet points."
    temperature: 0.3
    max_tokens: 200
    output_column: "Key_Strengths"

  - id: "step_3"
    name: "Key weaknesses"
    prompt: "Identify 3-5 competitive weaknesses or gaps in their offering. Where are they vulnerable? Format as bullet points."
    temperature: 0.3
    max_tokens: 200
    output_column: "Key_Weaknesses"

  - id: "step_4"
    name: "Pricing strategy"
    prompt: "Analyze and describe their pricing strategy: model (subscription, one-time, usage-based), positioning (premium, mid-market, budget), and approach."
    temperature: 0.3
    max_tokens: 150
    output_column: "Pricing_Strategy"

  - id: "step_5"
    name: "Target market"
    prompt: "Describe their primary target market: company sizes, industries, geographies, buyer personas. Be specific."
    temperature: 0.3
    max_tokens: 150
    output_column: "Target_Market"

  - id: "step_6"
    name: "Differentiation opportunities"
    prompt: "Based on their strengths and weaknesses, suggest 3-4 specific ways we could differentiate our offering from theirs."
    temperature: 0.5
    max_tokens: 250
    output_column: "Differentiation_Opportunities"

  - id: "step_7"
    name: "Threat level"
    prompt: "Assess their competitive threat level to our business: Critical, High, Medium, Low, or Minimal. Consider market overlap, capabilities, and momentum."
    temperature: 0.3
    max_tokens: 30
    output_column: "Threat_Level"

  - id: "step_8"
    name: "Strategic recommendation"
    prompt: "Provide strategic recommendation for how to compete against this competitor. Be specific and actionable."
    temperature: 0.4
    max_tokens: 200
    output_column: "Strategy_Recommendation"
```

### 14. Sales Call Notes Analyzer

**Use Case:** Extract insights from sales call notes

```yaml
id: business_002
name: "Sales Call Insights Extractor"
category: "business_intelligence"
context_columns: ["Account_Name", "Call_Date", "Sales_Rep", "Call_Type"]

steps:
  - id: "step_1"
    name: "Call summary"
    prompt: "Create a concise 2-3 sentence summary of this sales call capturing the main discussion points."
    temperature: 0.3
    max_tokens: 150
    output_column: "Call_Summary"

  - id: "step_2"
    name: "Key topics"
    prompt: "Extract the main topics discussed. Return as comma-separated list (max 5 topics)."
    temperature: 0.2
    max_tokens: 100
    output_column: "Topics_Discussed"

  - id: "step_3"
    name: "Pain points mentioned"
    prompt: "Identify specific pain points, challenges, or problems the prospect mentioned. List each distinctly."
    temperature: 0.3
    max_tokens: 200
    output_column: "Pain_Points"

  - id: "step_4"
    name: "Buying signals"
    prompt: "Identify any buying signals: budget discussions, timeline mentions, decision process details, stakeholder involvement, next steps commitment. List all signals found."
    temperature: 0.3
    max_tokens: 200
    output_column: "Buying_Signals"

  - id: "step_5"
    name: "Objections raised"
    prompt: "Identify objections or concerns raised by the prospect. List each objection clearly."
    temperature: 0.2
    max_tokens: 200
    output_column: "Objections"

  - id: "step_6"
    name: "Competitors mentioned"
    prompt: "Extract names of any competitors mentioned during the call. Return as comma-separated list, or 'None' if none mentioned."
    temperature: 0.1
    max_tokens: 100
    output_column: "Competitors_Mentioned"

  - id: "step_7"
    name: "Deal stage"
    prompt: "Based on the call notes, suggest appropriate deal stage: Discovery, Qualification, Demo, Proposal, Negotiation, Closing, or Unqualified."
    temperature: 0.3
    max_tokens: 30
    output_column: "Suggested_Stage"

  - id: "step_8"
    name: "Close probability"
    prompt: "Estimate likelihood of closing this deal based on call notes. Return percentage (0-100) followed by confidence level in parentheses. Example: '65 (Medium confidence)'"
    temperature: 0.3
    max_tokens: 50
    output_column: "Close_Probability"

  - id: "step_9"
    name: "Action items"
    prompt: "Extract all action items and next steps committed to during the call. Include who owns each action. Format as bullet points."
    temperature: 0.2
    max_tokens: 250
    output_column: "Action_Items"

  - id: "step_10"
    name: "Strategic insights"
    prompt: "Provide 2-3 strategic insights or recommendations based on this call. What should the sales rep focus on? What strategies would be most effective?"
    temperature: 0.4
    max_tokens: 200
    output_column: "Strategic_Insights"
```

---

## E-commerce

### 15. Product Review Analyzer

**Use Case:** Extract insights from customer reviews

```yaml
id: ecommerce_001
name: "Product Review Analysis"
category: "ecommerce"
context_columns: ["Product_Name", "Rating", "Reviewer", "Date"]

steps:
  - id: "step_1"
    name: "Sentiment classification"
    prompt: "Classify review sentiment: Positive, Negative, Neutral, or Mixed."
    temperature: 0.2
    max_tokens: 20
    output_column: "Sentiment"

  - id: "step_2"
    name: "Review authenticity"
    prompt: "Assess if this review appears authentic or suspicious. Return: Authentic, Potentially Fake, or Suspicious. Consider: specificity, language patterns, extreme claims."
    temperature: 0.3
    max_tokens: 30
    output_column: "Authenticity"

  - id: "step_3"
    name: "Aspects mentioned"
    prompt: "Identify specific product aspects mentioned: Quality, Price, Shipping, Customer Service, Design, Functionality, Durability, etc. Return as comma-separated list."
    temperature: 0.2
    max_tokens: 100
    output_column: "Aspects"

  - id: "step_4"
    name: "Positive highlights"
    prompt: "Extract what the customer liked most about the product. List specific positives mentioned."
    temperature: 0.2
    max_tokens: 150
    output_column: "Positives"

  - id: "step_5"
    name: "Negative issues"
    prompt: "Extract complaints or issues mentioned. List specific problems or concerns."
    temperature: 0.2
    max_tokens: 150
    output_column: "Negatives"

  - id: "step_6"
    name: "Feature requests"
    prompt: "Identify any feature requests or improvement suggestions in the review. Return 'None' if no suggestions."
    temperature: 0.3
    max_tokens: 150
    output_column: "Suggestions"

  - id: "step_7"
    name: "Use case"
    prompt: "Identify how the customer is using this product. What is their use case or application?"
    temperature: 0.3
    max_tokens: 100
    output_column: "Use_Case"

  - id: "step_8"
    name: "Helpfulness score"
    prompt: "Rate how helpful this review would be to other shoppers (1-10). Consider specificity, balance, detail, and relevance. Return only number."
    temperature: 0.3
    max_tokens: 10
    output_column: "Helpfulness"
```

---

## HR & Recruiting

### 16. Resume Screening & Analysis

**Use Case:** Analyze and score resumes

```yaml
id: hr_001
name: "Resume Screening Analysis"
category: "hr_recruiting"
context_columns: ["Candidate_Name", "Position_Applied", "Years_Experience"]

steps:
  - id: "step_1"
    name: "Experience summary"
    prompt: "Summarize the candidate's professional experience in 2-3 sentences, highlighting most relevant roles and achievements."
    temperature: 0.3
    max_tokens: 200
    output_column: "Experience_Summary"

  - id: "step_2"
    name: "Key skills"
    prompt: "Extract key technical and professional skills from this resume. Return as comma-separated list (max 10 skills)."
    temperature: 0.2
    max_tokens: 150
    output_column: "Key_Skills"

  - id: "step_3"
    name: "Education level"
    prompt: "Identify highest education level: High School, Associate, Bachelor, Master, PhD, or Not Specified."
    temperature: 0.1
    max_tokens: 30
    output_column: "Education_Level"

  - id: "step_4"
    name: "Role fit score"
    prompt: "Based on the resume content and position applied for, rate the candidate's fit for the role (1-10). Consider relevant experience, skills, and qualifications. Return only number."
    temperature: 0.3
    max_tokens: 10
    output_column: "Role_Fit_Score"

  - id: "step_5"
    name: "Career progression"
    prompt: "Assess career progression: Strong Growth (consistent advancement), Steady (stable progression), Lateral (moves but not advancement), Unclear, or Concerning (many short stints/gaps)."
    temperature: 0.3
    max_tokens: 30
    output_column: "Career_Trajectory"

  - id: "step_6"
    name: "Red flags"
    prompt: "Identify any red flags: employment gaps, many short tenures, skill mismatches, or other concerns. Return 'None' if no issues, otherwise list concerns."
    temperature: 0.3
    max_tokens: 150
    output_column: "Red_Flags"

  - id: "step_7"
    name: "Unique strengths"
    prompt: "Identify 2-3 unique strengths or standout qualities that differentiate this candidate."
    temperature: 0.4
    max_tokens: 150
    output_column: "Unique_Strengths"

  - id: "step_8"
    name: "Interview recommendation"
    prompt: "Recommend interview decision: Strong Yes (top candidate), Yes (qualified), Maybe (borderline), or No (not qualified). Include brief reasoning."
    temperature: 0.3
    max_tokens: 100
    output_column: "Interview_Recommendation"

  - id: "step_9"
    name: "Interview focus areas"
    prompt: "If interviewing this candidate, suggest 3-4 specific topics or areas to probe deeper. What should be validated or explored?"
    temperature: 0.4
    max_tokens: 200
    output_column: "Interview_Focus"
```

---

## Financial Analysis

### 17. Expense Categorization & Analysis

**Use Case:** Categorize and analyze business expenses

```yaml
id: financial_001
name: "Expense Intelligence"
category: "financial_analysis"
context_columns: ["Date", "Vendor", "Amount", "Department"]

steps:
  - id: "step_1"
    name: "Expense category"
    prompt: "Categorize this expense: Office Supplies, Software/SaaS, Travel, Meals & Entertainment, Marketing, Utilities, Rent, Salaries, Professional Services, Equipment, or Other."
    temperature: 0.2
    max_tokens: 50
    output_column: "Category"

  - id: "step_2"
    name: "Sub-category"
    prompt: "Provide more specific sub-category. Example: if category is 'Software', specify: 'CRM', 'Design Tools', 'Analytics', etc."
    temperature: 0.2
    max_tokens: 50
    output_column: "Sub_Category"

  - id: "step_3"
    name: "Recurring status"
    prompt: "Determine if this is a Recurring expense (monthly/annual subscription) or One-time expense."
    temperature: 0.2
    max_tokens: 20
    output_column: "Recurring_Status"

  - id: "step_4"
    name: "Business necessity"
    prompt: "Rate business necessity: Essential (critical for operations), Important (valuable but not critical), Nice-to-Have (beneficial but optional), or Questionable."
    temperature: 0.3
    max_tokens: 30
    output_column: "Necessity"

  - id: "step_5"
    name: "Cost optimization potential"
    prompt: "Assess potential for cost optimization: High (likely savings available), Medium (some optimization possible), Low (already optimized), or Unknown."
    temperature: 0.3
    max_tokens: 30
    output_column: "Optimization_Potential"

  - id: "step_6"
    name: "Flags and notes"
    prompt: "Flag any concerns: unusually high amount, duplicate expense, missing receipt, policy violation, needs approval, etc. Return 'None' if no concerns."
    temperature: 0.3
    max_tokens: 150
    output_column: "Flags"

  - id: "step_7"
    name: "Recommendations"
    prompt: "Suggest specific actions: alternative vendors, negotiation opportunities, usage optimization, or elimination. Be specific and actionable."
    temperature: 0.4
    max_tokens: 200
    output_column: "Recommendations"
```

---

## Template Usage Guide

### How to Use These Templates

1. **Select Appropriate Template**: Choose based on your data and objective
2. **Map Context Columns**: Ensure your data has the required context columns
3. **Adjust Parameters**: Modify temperature and max_tokens if needed
4. **Test on Sample**: Run on 5-10 rows first to validate results
5. **Review and Iterate**: Adjust prompts based on initial results
6. **Full Execution**: Process entire dataset
7. **Export Results**: Save enriched data with new columns

### Customization Tips

**Adjusting Temperature:**
- 0.0-0.2: Deterministic, factual tasks (categorization, extraction)
- 0.3-0.5: Balanced (analysis, scoring)
- 0.6-0.9: Creative tasks (content generation, brainstorming)

**Prompt Engineering Best Practices:**
- Be specific about output format
- Provide examples in prompts when helpful
- Use constraints (character limits, specific values)
- Chain steps logically (each builds on previous)
- Include fallback instructions ("Return 'Unknown' if uncertain")

### Creating Custom Templates

```yaml
id: custom_xxx
name: "Your Template Name"
category: "your_category"
description: "What this template does"
author: "Your Name"
version: "1.0"

context_columns: ["Required", "Context", "Columns"]

steps:
  - id: "step_1"
    name: "Step name"
    prompt: "Clear, specific instructions..."
    temperature: 0.3
    max_tokens: 150
    output_column: "Output_Column_Name"

validation:
  required_columns: ["Column1", "Column2"]
  output_columns: ["New_Column1", "New_Column2"]

metadata:
  estimated_time_per_row: "2s"
  api_calls_per_row: 3
  use_cases: ["Use case 1", "Use case 2"]
  tags: ["tag1", "tag2"]
```

---

## Template Performance Guide

### Estimated Execution Times

| Template | Steps | API Calls/Row | Time/Row | 1000 Rows |
|----------|-------|---------------|----------|-----------|
| Complete Data Cleanup | 4 | 4 | ~2-3s | ~40 min |
| Email Validation | 5 | 5 | ~2.5s | ~42 min |
| Sentiment Analysis | 5 | 5 | ~2.5s | ~42 min |
| Customer Feedback | 7 | 7 | ~4s | ~67 min |
| Product Description | 7 | 7 | ~4-5s | ~75 min |
| Social Media Suite | 6 | 6 | ~3.5s | ~58 min |
| Company Enrichment | 7 | 7 | ~4s | ~67 min |
| Lead Scoring | 8 | 8 | ~4.5s | ~75 min |
| Competitive Analysis | 8 | 8 | ~5s | ~83 min |
| Resume Screening | 9 | 9 | ~5-6s | ~90 min |

*Times assume OpenAI API with typical latency. Ollama may be faster or slower depending on hardware.*

---

## License

These meta prompt templates are provided under MIT License for use with Excel AI Assistant.

**Credits:** Template library created for Excel AI Assistant v2.0
