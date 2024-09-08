i will document my prs here

---

# 8/30/24

## Change files in data uploads admin

https://github.com/GoliathData/sourcing/pull/937

- Added the 'Change File' button to the data uploads tab for admins
- Created a new ChangeFile button component. This is in the top right of the Data Upload sheet for admins. Clicking this and selecting a file will replace the current file processing task's file.

* The newly uploaded file will not retain the old file's name which will confuse users. Change this.
* The file upload code on the frontend is repeated in lot's of places and is messy. Refactor this.

## Script to ingest notices from Propview

https://github.com/GoliathData/sourcing/pull/938

- A user from Virginia signed up where we have no data. Austin got files from Propstream and Propview, and I made a script to ingest them. This script:
  - Takes each row of the csv and makes a string of column names to their values. It then creates a public notice with this string as the rawNoticeText.
  - This then will flow through the normal data ingestion pipeline.

* I accidentally pushed straight to mine and deployment failed, but this whole script ends up getting deleted anyway, for reasons discussed in PR 943

## Add credits to users balance when the subscribe

https://github.com/GoliathData/sourcing/pull/939

- When a user subscribes to:
  - Basic give them $50
  - Pro give them $150
  - Enteprise give them $500

* This code calls `initializeOrganizationBalance()` which doesen't really make sense. We should have a new function that adds the credits to the balance.

## Don't let users filter by counties where they dont have approved access

https://github.com/GoliathData/sourcing/pull/940

- Self explanatory.

* If they have no approved access to any counties, they by default get access to all counties. (Austins idea. this doesent really make sense because we'll give them access to all counties, but then later take access away from them? I feel like we should give them no access by default, and then give them access to the counties they have approved access to.)

## UI of notices for Free/Basic/Pro users

https://github.com/GoliathData/sourcing/pull/941

- Users were able to press more info, go to notices tab and copy and paste to see the text under the blur. Fixed this.
- The lock over the blur was centered over the notice.

## Fixed problems from PR 940

https://github.com/GoliathData/sourcing/pull/942

- When the user had no approved access to any counties, it defaulted to fetching all counties. This was fine on the all properties but in admin tools when fetching all organizations that query was so slow it timed out.
- Now instead, it returns an empty list, and on the frontend we get counties from app/public/data/counties_with_data.json

## Table GPT

https://github.com/GoliathData/sourcing/pull/943

- I'll explain the chain of thought leading to me adding this:
  - I looked at our spending on OpenAI today and for the 2456 notices we ingested from that first file from the script in PR 938, we spent like 60$. And Austin had handed me like 2 more files with like 6000 more notices. So i was like, we can't keep doing this.
  - What we should do is have the same thing as Bulk Skip Tracing, where we can select and map columns from a csv file to the value they should occupy in the public notice and notice enrichment objects.
  - So both these features are built on the same thing, so in this PR i build an abstract class that really has two functions: `selectRelevantColumns()` and `mapColumnsToInternalHeaders()`. Concrete classes must define the enum of their internal headers, and any heuristics they may want to use before using chatgpt. calls to chatgpt are batched to avoid overwhelming chatgpt with too many options and ran concurrently with plimit.

* In this pr i just made the abstract class and changed BulkSkipTraceService to inherit from it. In a later PR ill add the new class for ingesting notices.
* I'll add the same ui in bulk skiptrace to the data upload sheet for admins. We can do this manually, and adjust heuristics and prompts until its reliable enough for us to let it run automatically.

---

# 9/1/24

## Table GPT 2 (renamed to ColumnSelectorService and ColumnClassifierService)

https://github.com/GoliathData/sourcing/pull/945
I'm continuing work on table gpt. To reiterate, tablegpt is responsible for the classification of a csv file's columns into an enum value we define.

I tried looking at LLAMA-index, langchain, some other open source code and used exa, perplexity and chatgpt to search for a similar tool that we could use but I couldn't find anything.

A few decisions I made:

- Context: For context, lets give the LLM not just the column names but also the first row of data.
- Chunking: We don't want to overwhelm the LLM with too many columns at once. We can use chunking to give the LLM a manageable number of columns at once.
- Nonflat structures:
  For example, when we receive a csv in data enrichment, we could imagine a csv that has columns for multiple owners.
  | Address | Owner 1 First Name | Owner 1 Last Name | Owner 2 First Name | Owner 2 Last Name |

  In this scenario we will simply have the LLM classify columns as `Owner First Name` and `Owner Last Name`. This means the output of TableGPT can map multiple columns to the same enum value. This avoids difficult problems like having to make smarter chunking. TableGPT is not responsible for grouping. It is merely classifying columns

---

# 9/2/24 - 9/3/24

## Process csv data from data cleaning, and integrate with data enrichment pipeline

https://github.com/GoliathData/sourcing/pull/947
The admin sheet in data uploads now has a new option to run data cleaning as opposed to BEM. (the ui is shit, in the sheet)

This button will open the same csv pipeline UX as we had for bulk skiptrace, where it goes through column selection and classification, but now for data cleaning fields (`DataCleaningColumnType` in schema.gql)

Now, given the csv and column classifications we need to integrate with the data enrichment pipeline.

The specific step of the pipeline we will enter into is the Entity Extraction. Reason being, we obviously skip the Scraping step, and we don't need to run the enrichment step because the data is already semi structured.

But theres still a few things we need to do before we can run entity extraction. Ultimately we want to create an object of the same shape as what GPT extraction and BEM outputs, so that we can pass it into the Entity Extraction step.

Namely, we need to:

- The csvs rows has strings - we need to convert these to enums
- We need to group owner names, mailing addresses, phone numbers and emails together
- We need to differentiate owners into entities and people

Now i wont get into too much detail but ill say this. This logic mentioned above uses heuristics, and as a fallback or in some places where theres no better way to decide, it uses GPT. The heuristics are built on top of assumptions - all of which are written as docstrings in the code. For every csv ill upload ill manually review the assumptions and adapt the code as needed. I believe there is a point where this just becomes self sufficient, but for the sake of getting this code out fast i took this route. either way, only admins will be able to use this.

Last thing to mention - this code can definitely be refactored. i just wanted to get it out fast - and i did test it thoroughly to make sure it works.

Only one problem remains. I ran this locally and got this:
17:41:24.246 [info] Finished processing CSV data
{ processedCount: 2119, errorCount: 0 }
Problem here is when we run it in prod the instance will time out. Luckily its easy to recover - we can easily get the greatest source grn that starts with this source grn and then resume from that row in the csv. however this would mean allowing the instance to fail, and requiring a cron job to scan for statuses and blah blah blah. lots of bullshit.

i think a better solution is just - have a constant variable that looks at how much time this instance has. when this instance is getting close to the end of its time, we can just gracefully send a message back to the pubsub with the file processing task id and the last row it finished on and gracefully exit. i like this because itll be easier to implement. and so i shall.

---

# 9/3/24

## Decoupling data cleaning csv

https://github.com/GoliathData/sourcing/pull/949

Report:
Process csv data in chunks, respecting the cloud function timeout limits.
Transactions on statuses to ensure idempotency.
Strengths: 1. Scalability: The solution can handle large CSV files by processing them in chunks, respecting the cloud function timeout limits. 2. Concurrency: Using pLimit allows for controlled parallel processing of rows. 3. Error Handling: Comprehensive error catching and logging throughout the process. 4. Graceful Timeout Handling: The system exits gracefully when approaching the timeout, ensuring no data is lost. 5. Flexibility: The column mapping step allows for dynamic handling of different CSV structures.
Potential Improvements: 1. Memory Management: As you mentioned, loading the entire CSV into memory could be a bottleneck for extremely large files. Consider implementing streaming for CSV reading. 2. Progress Tracking: Implement a mechanism to track overall progress across multiple function invocations. (sourcegrn does this already actually) 3. Retry Mechanism: Add a retry system for failed row processing. 4. Performance Optimization: Profile the code to identify any performance bottlenecks, especially in the row processing logic.

---

# 9/4/24 - 9/5/24

# Fixing csv pipeline bugs

https://github.com/GoliathData/sourcing/pull/952/files
https://github.com/GoliathData/sourcing/pull/955
https://github.com/GoliathData/sourcing/commit/03174650634b2f468d877d32b20a5d071778b68a
https://github.com/GoliathData/sourcing/commit/efeb1cf6b41bfc52e4ce57eae86c39e8258aeedb

All of these commits are fixing bugs in the csv pipeline i implemented yesterday. Austin gave me a lot of files and i was running each and encountering and fixing backend bugs, ui/ux bugs/improvements and just yeah, debugging.

---

# 9/5/24

# Token Usage Tracking Implementation

https://github.com/GoliathData/sourcing/commit/abbe042581dd9eefc2c374678c9ffa12f463ffc0

i made this csv pipeline because previously we passed each row of the csv directly to the LLM, which was expensive. then the technique of mapping fields in the csv columns to fields in our objects was much cheaper. but then after i made this pipeline it got like really expensive again and i was like wtf? I had to look at the instructor response's metadata to see that name extractions longass system prompt was the cause. anyway that prompted me to build this token usage tracking so we can better track our token usage.

Key Changes:
Added TokenUsage model to Prisma schema
Added token usage tab to admin tools

For now this is completely fine, but in the future we should have a cron job that updates the accumulated token usage at time stamps so we can do prefix sums which will be super efficient
