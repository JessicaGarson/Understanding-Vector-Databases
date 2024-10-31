## Install the required packages
## pip install -qU elasticsearch langchain langchain-elasticsearch langchain-openai
from langchain_elasticsearch import ElasticsearchRetriever
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import format_document
from langchain.prompts.prompt import PromptTemplate
import os
es_client = Elasticsearch(
    "https://8cc06090c29a4937a47701d448a541bd.us-east4.gcp.elastic-cloud.com:443",
    api_key=os.environ["ES_API_KEY"]
)
      
def build_query(query):
    return {
        "retriever": {
            "standard": {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "text"
                        ]
                    }
                }
            }
        }
    }
index_source_fields = {
    "vr_tour_data": "text"
}
retriever = ElasticsearchRetriever(
    index_name="vr_tour_data",
    body_func=build_query,
    content_field=index_source_fields,
    es_client=es_client
)
model = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"], model_name="gpt-3.5-turbo")
ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """
  Instructions:
  
  - You are an assistant for question-answering tasks.
  - Answer questions truthfully and factually using only the context presented.
  - If you don't know the answer, just say that you don't know, don't make up an answer.
  - You must always cite the document where the answer was extracted using inline academic citation style [], using the position.
  - Use markdown format for code examples.
  - You are correct, factual, precise, and reliable.
  
  Context:
  {context}
  
  """
)
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")
def _combine_documents(
    docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)
_context = {
    "context": retriever | _combine_documents,
    "question": RunnablePassthrough(),
}
chain = _context | ANSWER_PROMPT | model | StrOutputParser()
ans = chain.invoke("what is the nasa sales team?")
print("---- Answer ----")
print(ans)