# Data Science with Multiple Agents - The Look Ecommerce public data set and Customer Demographics example (Using dummy data)

## Overview

This agent is a **multi-agent data science system** based on the **data-science** agent in available in this repo, that handles complex data analysis tasks. Its core function is to orchestrate specialized sub-agents to perform various steps in a data science pipeline, from data retrieval to machine learning.

The key features of this agent are:

* **Multi-Agent Architecture:** A top-level agent directs specialized sub-agents for different tasks, such as:
    * **NL2SQL:** A Database Agent translates natural language into SQL to interact with BigQuery.
    * **NL2Py:** A Data Science Agent performs data analysis and visualization using Python.
    * **BQML:** A BQML Agent trains and evaluates machine learning models directly in BigQuery.

## This version adds the following capabilities.

* **Multi-Dataset Management:** The agent can connect to and query multiple BigQuery datasets.
* **Contextual Inference:** The agent uses an advanced reasoning capability to determine which dataset(s) to query based on the user's natural language question, eliminating the need for the user to specify the data source.
* **Rich Output:** It can generate both text-based responses and visual outputs like plots and graphs for data exploration and analysis.

## 1. Single Data Set questions
## From thelook_ecommerce dataset

These questions require the agent to query only tables within the thelook_ecommerce public dataset. They are great for testing basic SQL functionality like SELECT, WHERE, GROUP BY, and COUNT.
Order and Product Analysis:
"How many distinct products were sold in the last 30 days?"
"What is the total revenue for each product category?"
"List the top 10 most expensive products."
"Find all orders that were shipped to 'New York'."
"What is the average sale price of a t-shirt?"
User and Traffic Analysis:
"How many new users signed up in January 2024?"
"Which distribution center has the most items shipped from it?"
"What is the total number of unique visitors to the website in the last week?"
"Show the total number of orders placed by each customer."

## From customer_profiles dataset

These questions focus on the newly created customer_profiles dataset, testing the agent's ability to query it independently.
Demographic Insights:
"How many customers are in each age_group?"
"What is the distribution of household_income among our customers?"
"List all customers who live in the 'South' region."
Survey and Feedback Analysis:
"What is the average satisfaction_score from all survey responses?"
"Show me all the feedback text from surveys with a satisfaction_score of 1."
"Count the number of survey responses for each purchase_intent category ('High', 'Medium', 'Low')."
"Find the id of the user with the most recent survey submission."

## 2. Questions for Joins 🤝

These questions require the agent to explicitly join data from thelook_ecommerce and customer_profiles on a common key (id) to answer direct business questions.
Customer Demographics & Order Value: "What is the average order value for customers in the 'Midwest' region, and how does it compare to the 'Northeast'?"
Product Performance & Gender: "Show me the top 5 most purchased products by customers who identify as 'Female'."
Satisfaction & Purchase History: "Create a table showing the average number of orders and average total spend for each satisfaction_score (1-5) based on customer survey data."
Age Group & Refund Rate: "Calculate the refund rate (number of refunded items / total items sold) for the '18-25' age group. How does this compare to the 56+ age group?"
Income & Discount Usage: "What percentage of orders used a discount for customers in the '$100k+' household income bracket?"

## 3. Questions for Contextual Inference 🤔

These questions are more open-ended and require the agent to first infer which dataset contains the necessary information before formulating a multi-table query.
Popularity by Demographics: "Which clothing category is most popular among customers with a household_income of '$50k - $100k'?"
Geographic Shopping Habits: "Do customers in the 'West' region tend to buy more clothing for 'men' or for 'women'?"
Feedback & Product Type: "Analyze customer feedback for orders of 'Activewear'. What is the average satisfaction_score for this product category?"
Purchase Intent & Recency: "Identify the top 10 customers who gave a 'High' purchase_intent score in their last survey but haven't placed an order in the last 60 days."
Correlation Analysis: "Is there a correlation between a customer's satisfaction_score and their total number of purchases?"

## 3. Questions for BQML Prediction 🤖

These questions test the agent's ability to combine data from both datasets to train and analyze machine learning models using BigQuery ML (BQML).
Predicting Customer Lifetime Value (CLV):
"Using the transaction data from thelook_ecommerce and the demographic data from customer_profiles, train a BigQuery ML model to predict a customer's lifetime value. What are the most important features that influence the prediction?"
Churn Prediction:
"Can you build a model to predict customer churn? Use customer survey data (customer_profiles.survey_responses) and purchase frequency from thelook_ecommerce to train a BQML model. Identify which factors are most predictive of a customer leaving."
Predicting High-Value Customers:
"Using a boosted tree classifier, predict which customers are likely to become 'high-value' customers (top 20% by total spend). Combine purchasing history with their household income and region to create the training data."

## Data Sets
We use the **"thelook_ecommerce"** BigQuery public dataset.

It's a popular, publicly available dataset that's great for learning and practicing SQL, especially for e-commerce analytics. Here are some key things to know about it:
* **Fictitious Data:** The dataset contains synthetic (not real) data for a fictional clothing e-commerce site created by the Looker team. This makes it a safe and privacy-preserving resource for analysis.
* **Publicly Hosted on BigQuery:** Because it's a public dataset hosted on Google BigQuery, you can access and query it for free (within the free tier of BigQuery). This makes it an excellent resource for anyone with a Google Cloud account to get hands-on experience with BigQuery.
* **Comprehensive Information:** It includes several tables with information on various aspects of an e-commerce business, such as:
    * Customers
    * Products
    * Orders and Order Items
    * Web events
    * Digital marketing campaigns
    * Logistics and distribution centers

We also use a **customer demographics** and survey data dataset, to test your data science agent's capabilities, requiring the agent to perform joins, comparisons, and contextual inference across both.

**Rationale**
An excellent additional dataset to test your data science agent's capabilities would be one that complements `the thelook_ecommerce` dataset, requiring the agent to perform joins, comparisons, and contextual inference across both. A customer demographics and survey data dataset would be a great choice.

The thelook_ecommerce dataset is rich in transactional and product information, but it lacks detailed customer-specific data like age, income, household size, or feedback. By creating a second dataset with this information, you can pose questions that require the agent to:

* **Perform Joins:** To answer questions like "What is the average order value for customers in the 30-40 age group?", the agent would need to join the new customer demographics dataset with the thelook_ecommerce orders or order_items tables based on a shared customer ID.
* **Contextual Inference:** Questions such as "Which product category is most popular among high-income earners?" would force the agent to infer which dataset to query for customer income information and which to query for product category data, then combine the results.

* **Advanced Analytics:** You could ask for a machine learning model (using BQML) to predict a customer's lifetime value based on their demographic information and purchasing history. This would require the agent to pull features from both datasets.

## Customer Demographics Dataset

* **Step 1: Create the Dataset**
First, you need to create a new dataset to house the new tables. I'll name it customer_profiles.

```bash
CREATE SCHEMA IF NOT EXISTS `your_project_id.customer_profiles`
OPTIONS(
  location='US',
  description='Dataset to store customer demographic and survey data, complementing the thelook_ecommerce dataset.'
);
```
* **Step 2:Create the demographics Table**
```bash
CREATE TABLE IF NOT EXISTS `your_project_id.customer_profiles.demographics` (
    user_id INT64,
    age_group STRING,
    household_income STRING,
    gender STRING,
    region STRING
);
```

* **Step 3: Create the survey_responses Table**
```bash
CREATE TABLE IF NOT EXISTS `your_project_id.customer_profiles.survey_responses` (
    survey_id INT64,
    user_id INT64,
    response_date TIMESTAMP,
    satisfaction_score INT64,
    feedback_text STRING,
    purchase_intent STRING
);
```
After running these queries, you will have an empty dataset with the defined tables. You can then populate these tables with some mock data to begin testing your agent's ability to handle multi-dataset queries.

## Disclaimer

This agent sample is provided for illustrative purposes only and is not intended for production use. It serves as a basic example of an agent and a foundational starting point for individuals or teams to develop their own agents.

This sample has not been rigorously tested, may contain bugs or limitations, and does not include features or optimizations typically required for a production environment (e.g., robust error handling, security measures, scalability, performance considerations, comprehensive logging, or advanced configuration options).

Users are solely responsible for any further development, testing, security hardening, and deployment of agents based on this sample. We recommend thorough review, testing, and the implementation of appropriate safeguards before using any derived agent in a live or critical system.

