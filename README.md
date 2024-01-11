# Russian Ukraine Conflict Knowledge Store #

This project is focused on creation of a custom knowledge store about the Russian and Ukraine conflict.  It serves three audiences:

- Those with an interest in the Russian and Ukraine conflict,
- Those who want to learn how to create a custom knowledge store relevant to a heterogeneous set of documents,
- Those who want to know "How good are LLMs at auto-generating code?"

It uses a 240 page chronology of the major events of the conflict as the knowledge store core.  This open source document was developed by researchers at the National Security Archives.  It is the best open source chronology of the conflict's events through May 2023.  Critically, it contains links to the original articles where the event summaries were distilled from.  Here is a link to the PDF chronology document: 

[Cyber Vault Ukraine Timeline](https://nsarchive.gwu.edu/document/29562-cyber-vault-ukraine-timeline)

The project ingests this file and all files it points to via hyperlinks.  This leads to a knowledge store with close to 700 documents in total.

## Creating the Document Set for the Knowledge Store ##

The project transforms the PDF into a knowledge base in three discrete steps depicted in the following figure.

![Steps to Create the Russia Vs. Ukraine Knowledge Store](images/KnowledgeStoreCreation.png)

**1. Transform**

This step takes the PDF and transforms it into a CSV file. This required identifying the dates, the narratives, and collecting the URLs for the linked documents from the PDF.  The generated CSV file is not 100% precise as some rows do not represent specific events.  This is due to the regex over-identifying dates.  However, it is certainly able to genereate a very good CSV representation (around 98% accurate) of the original pdf that contains: 1. Date, 2. Description, and 3. Supporting URLS for event descriptions.  This CSV provides the core set of documents for the knowledge store.

**2. Collect**

This step downloads the supporting documents from the Internet.  Documents will only be downloaded if they still exist and are not pay-wall blocked.  The files are stored locally.  PDFs are stored in their raw form.  HTML pages are stored as text extraction representations wrapped in JSON.  The project uses Python threads to download the resources pointed to by URLs.

**3. Create**

The final step is to create a knowledge store.  The project simply embeds the document corpus using OpenAI's `text-embedding-ada-002` model.  A vast majority of the text in the collected documents is well-written, English narratives.  The `text-embedding-ada-002` model does quite well at embedding the documents for question and answering.  The projet provides three examples of how to use the embedded documents. It demystifies what is meant by "context" and what a custom knowledge store is really all about.

## Installation and Running the Code ##

The code is a Python project.  

**Step 1. Install requirements.txt**

The project contains a requirements.txt.  For those who are unfamiliar - here are some directions on how to use a requirements file to manage libray usage by a Python project:

https://chat.openai.com/share/7b1848d5-b89a-4e99-8b6b-e65238aea72c

**Step 2. Update config file**

The `scripts` folder holds the project source code. The folder holds a file named `config.ini`.  It provides the following variables the user needs to configure.  Some of the default values assume the user creates a folder within the `scripts` folder named `files`.  All directory realted values in the default configuration are relative to this directory.

- `NSA_PDF_TIMELINE` = Path to Ukraine timeline PDF file
- `NSA_CSV_LOCATION` = Path to CSV file that the timeline PDF is translated into.
- `PDFS_FOLDER` = Folder that holds the downloaded PDF files.
- `JSONS_FOLDER` = Folder that holds the web page text extractions wrapped in JSON.
- `OPENAI_API_KEY` = An Open AI key.  Be careful with it!  Don't share it!
- `CHROMA_DB_PERSIST` = Folder that holds the chroma db.  

**Step 3. Create events timeline CSV file**

The scripts folder contains a file named `Driver.py`.  This script drives creation of the CSV file, downloads the files and web pages links point to, and creates the knowledge store.

To run the CSV creation, simply enable and run the function at bottom of `Driver.py`  named `createCSV` (commented with #1 in the file).  The config variables `NSA_PDF_TIMELINE` and `NSA_CSV_LOCATION` must be set.

The function will generate a file named `RussiaVsUkraineEventTimeline.csv`.  It will hold a CSV version of the PDF.  The file will be located in the `files` folder if the default configuration values are used.

**Step 4. Download resources for supporting URLs**

The timeline CSV file holds pointers to over a thousand links that are web pages or PDF documents with supplemental and more detailed information of the events in the timeline.  These represent the perfect content for a knowledge store.

The python class `Driver.py` contains instances of `PdfDownloader` and `HtmlDownloader`.  These are logically named and will download the PDFs and web pages the URLs point to.  The `config.ini` file contains two vairables: 

- `PDFS_FOLDER` = Folder that holds the downloaded PDF files.
- `JSONS_FOLDER` = Folder that holds the web page text extractions wrapped in JSON.

Here, the values point to two folders.  The default configuration assumes the folders are created inside the `files` folder like so: `scripts/files/pdffiles`.  Users are free to set the download location to wherever they wish.

A note about downloads.  Some sites no longer function and the original web pages and PDFs result in 404 errors.  Some web pages are paywalled blocks.  But a reasonable percentage (70%) are available for download with relevant content in tact.

HTML pages are scraped using BeautifulSoup.  Here, the implementation is basic.  No effort has been made to fine tune and strip out text exclusively relative to the Russian vs. Ukraine conflict.  

To run the download scripts, simply enable #2 and #3 in the script `Driver.py`.

**Step 4. Creating the Knowledge Store**

This is the goal of the project; creation of a knowledge store.   The folder `knowledge_store_examples` contains a series of progressively complex examples of question and answering.  

To run these demos the user will need a OpenAI key.  The key will need to be set in the config file (do not share it!).  It is accessed like so in the code:

`os.environ['OPENAI_API_KEY'] = openai_key`

Here are descriptions of each of the question and answering examples:

***Text as Context Only***

To run this demo, enabled #4 in the `Driver.py` class.

`TextAsContext.py` is the simplest case.  Here, each row of the `RussiaVsUkraineEventTimeline.csv` file is turned into a LangChain Document.  The first 100 rows of the document are used as context when a question is submitted to an LLM backed Question and Answering chain.  In a nutshell this is what happens:

- The script takes the first 100 rows and sends them as LangChain Documents to the ChatGPT 3.5 model,
- ChatGPT then uses that text (the 100 documents) as context to answer the question.  

The drawback to this approach is that the number of tokens that may be sent as context is capped (4,096 tokens maximum, for example).  That means a user cannot send the complete `RussiaVsUkraineEventTimeline.csv` file as context even if the user wanted to!  What a terrible limitation!

This example has a hard coded question for the purposes of demonstration: _How does Russia attempt to control the Internet?_

_Note: The OpenAI Cost Using ChatGPT 3.5 to run this demo:  Fraction of a cent_

***Vector Store as Context Unpersisted***

To run this demo, enabled #5 in the `Driver.py` class.

How does the user overcome the problem with sending tokens to ChatGPT to use as context?  One way is to create a custom, local knowledge store.  `VectorStoreAsContextUnpersisted.py` shows how to index the `RussianVsUkraineEventTimeline.csv` file using the OpenAI embeddings and a ChromaDB vector store.  What is happens is the following:

- Each row of `RussianVsUkraineEventTimeline.csv` is turned into a LangChain Document, 
- Each document is embedded in a vector space using the default OpenAI embeddings.  This makes it searchable as though it were another document indexed by ChatGPT.  

The user can now ask a question of the local knowledge store.  It is hardcoded with the question: _What is the IT Army?_

The (clear) drawback of this approach are the fact that the ChromaDB needs to be recreated each time.  This itself takes time and money!  The solution that is needed is one that persists the generated embedding.  See the next demo class!

_Note: The OpenAI Cost Using ChatGPT 3.5 to run this demo:  A few cents if that_

***Vector Store as Context Unpersisted***

To run this demo, enabled #6 in the `Driver.py` class.

The class `VectorStoreAsContextPersisted.py` creates embeddings for all the PDF files, the HTML extractions, and the `RussiaVsUkraineEventTimeline.csv`.  This means the user will have a much larger ChromaDB that will cost slightly more to generate.  

The first time it is run, a ChromaDB will be created in a folder called `files\chromadb` (assuming the user uses the config defaults).  The database will take some time to generate.  Subsequent runs will use this persisted ChromaDatabase as the knowledge store for a question answering.

The image shows the running script.  

![Questions and Answers with Provenance](images/QA_Example.png)

Here, a user has entered a question.  It is a typical LLM backed question / answering system.  The context of the question helps to define the expressiveness of the answer.  

Also note the section at bottom that lists provenance.  It includes the list of documents from the ChromaDB that it used to answer the question.  This is a critical piece of the puzzle - Does the LLM report where its answer came from?  In the example image above, 3 documents were used to create the answer.

_Note: The OpenAI Cost Using ChatGPT 3.5 to run this demo:  Under a dollar.  It is a onetime expense as once the ChromaDB is created, it is persisted._

## Use of Automated Code for Data Assembly & Cleaning ##

Most of the code found in this repository was auto-generated using LLMs ChatGPT, Claude, Ollama, and the LangChain chat agent. It is (_very_) safe to say that this project would not exist without these incredibly useful tools.  The matrix below lists how LLMs were used to auto-generate significant portions of the application's business logic:

| Task                                                                                                                             | Description of how LLM Assisted                                                                                                                                                                    |
|----------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Extract text from a PDF                                                                                                          | LLMs offered up multiple libraries in Python capable of text extraction from PDF.  Some are better than others.  The LLM's re-engineered this code until the best extraction library routine was identified. |
| Extract links from a PDF                                                                                                         | This is a pretty hard task to do for those unfamiliar with PDF manipulation.  It was much faster to have the LLM offer a solution than to search Google.                                           |
| Explain how a URL hyperlink in a PDF file may be bound to its text mention in the doucment                                       | This is is an extremely hard task!  A 20 minute discussion with an LLM described how it works.  It would have not been fun or easy to find this soultion using Goolge exclusively.                 |
| Provide regexes to find 30 different date patterns                                                                               | This task would have taken quite a long time to do manually.  Online regex tools would been consulted to test developed solutions.  The LLMs simply gave back solutions with most working on the intial request. |          
| Download the supporting PDF files and HTML pages                                                                                 | A relatively easy task - but why not let the LLM do it!                                                                                                                                            |
| Multi-thread downloads in Python                                                                                                 | Multi-threading is a moderately difficult task.  The LLM nailed how to do it in Python out of the box.                                                                                             |
| Extract text from HTML pages                                                                                                     | A moderately difficult task.  This led to many conversations about what was and was not possible.  The solution is not perfect - but text extraction from web pages rarely is.                     |
| Embedding the PDF documents, the timeline doucment, and web page extractions in a vector space for an LLM model, like Chat GPT 3 | The LangChain chat agent was good at describing the different apporaches to embedding documents using existing language models.                                                                    |
| Create a chromaDB for a question/answering (Q/A) chat agent                                                                      | There are so many new libraries and technologies with scant documentation.  After much cajoling - the LangChain chat agent expalined how to create and use the Chroma db as part of a Q/A agent!   |

One note about the genreated source code; there are no unit tests.    The project was initially created as a proof of concept.  Like so many proof of concept implementations, unit tests were not on the top of the list of tasks.  However, it is trivial to mandate the LLM generate unit tests along with the code it creates.  In the future there will be unit tests.

## Next Steps ##

There are many.  A short list of next steps inlcudes:

- Adding interview transciptions to the knowledge store.  This is critical.  Many of the articles mention speeches or interviews.  It would be trivially easy to use OpenAI's Whisper to translate the audio to text and then provide those as additional documents.
- Adding Langchain Agents and Templates. This would be focused toward development of a soup-to-nuts report authoring capability.  It is more advanced and would require question chaining and developing different sections of a report.
- Adding an abiity to grow the timeline.  This is certainly in the 'more to come' section for sure!  There is a path to getting the LLMs to search content and keep the timeline updated.